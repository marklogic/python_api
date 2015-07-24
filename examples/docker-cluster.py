#!/usr/bin/python3

import sys
import re
import os
import json
import pwd
import logging
import argparse
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
from marklogic.models.host import Host
from marklogic.models.connection import Connection
from marklogic.models.utilities.exceptions import *

class Docker:
    def __init__(self):
        self.marklogic = None
        self.uname=pwd.getpwuid(os.getuid()).pw_name
        self.adminuser="admin"
        self.adminpass="admin"
        self.realm="public"
        self.imatch="ml[0-9]"
        self.bootimage=None
        self.localimage=False
        self.count=None
        self.couple=None
        self.couple_user=None
        self.couple_pass=None
        self.name=None
        self.blacklist_file="/tmp/{0}.docker.skip".format(self.uname)
        self.blacklist={}
        self.container_list=[]
        self.containers={}
        self.localip=None
        self.ipaddr={}

    def set_credentials(self,user,password):
        self.adminuser = user
        self.adminpass = password

    def set_realm(self,realm):
        self.realm = realm

    def set_image_match(self,match):
        self.imatch = match

    def set_boot_image(self,image):
        if self.bootimage is not None:
            print ("Only one of -b or -B may be specified.")
            sys.exit(1)
        self.bootimage = image
        self.localimage = (image == "localhost")

    def set_count(self,count):
        self.count = count

    def set_couple(self,couple):
        self.couple = couple

    def set_couple_credentials(self,user,password):
        self.couple_user = user
        self.couple_pass = password

    def set_name(self,name):
        self.name = name

    def setup_cluster(self):
        if self.couple is not None and self.couple_pass is None:
            self.couple_pass = self.adminpass
            self.couple_user = self.adminuser

        self.find_containers()

        if not self.container_list:
            print("There must be at least one unused container running.")
            sys.exit(1)

        if self.localimage:
            ps = os.popen("docker exec " + self.container_list[0] + " ip route")
            for line in ps.readlines():
                match = re.match("^default via (\S+)", line)
                if match:
                    self.localip = match.group(1)
            if self.localip is None:
                print("Cannot find IP address of localhost!?")
                sys.exit(1)

        # Find the bootstrap image

        if self.localimage:
            pass
        else:
            if self.bootimage:
                found = False
                for key in self.containers:
                    image = self.containers[key]
                    if not found and \
                        (key == self.bootimage or re.match(self.bootimage, image)):
                        self.bootimage = key
                        found = True
                for key in self.ipaddr:
                    image = self.ipaddr[key]
                    if not found and image == self.bootimage:
                        self.bootimage = key
                        found = True
                if not found:
                    print("Cannot find boot image: {0}".format(self.bootimage))
                    sys.exit(1)
            else:
                self.bootimage = self.container_list[0]
                self.container_list.remove(self.bootimage)

        self.display_info()

        # Initialize the bootstrap image, if necessary

        if self.localimage:
            bootip = self.localip
        else:
            bootip = self.ipaddr[self.bootimage]

        if self.ml_init(bootip, self.bootimage):
            self.ml_security(bootip)

        conn = Connection(bootip, HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        if self.count is not None:
            self.count -= 1

        for container in self.container_list:
            if container == self.bootimage or container in self.blacklist:
                continue
            if self.count is not None and self.count <= 0:
                continue

            ip = self.ipaddr[container]
            self.ml_init(ip, container)
            self.ml_join(bootip, ip)

            if self.count is not None:
                self.count -= 1

        if self.name is not None:
            print("{0}: rename cluster...".format(bootip))
            cluster = self.marklogic.cluster()
            cluster.set_cluster_name(self.name)
            cluster.update()

        if self.couple is not None:
            print("{0}: couple with {1}...".format(bootip,self.couple))
            altconn = Connection(self.couple,
                                 HTTPDigestAuth(self.couple_user,
                                                self.couple_pass))
            altml = MarkLogic(altconn)
            altcluster = altml.cluster()
            cluster = self.marklogic.cluster()
            cluster.couple(altcluster)

        print("Finished")

    def ml_init(self, ip, container):
        print("{0}: initialize host {1}...".format(ip,container))
        try:
            host = MarkLogic.instance_init(ip)
        except UnauthorizedAPIRequest:
            # Assume that this happened because the host is already initialized
            host = Host(ip)

        self.blacklist[container] = 1
        self.save_blacklist()
        return host.just_initialized()

    def ml_join(self, bootip, ip):
        print("{0}: join cluster with {1}...".format(ip,bootip))
        cluster = self.marklogic.cluster()
        host = Host(ip)
        cluster.add_host(host)

    def ml_security(self, ip):
        print("{0}: initialize security...".format(ip))
        MarkLogic.instance_admin(ip,self.realm,self.adminuser,self.adminpass)

    def load_blacklist(self):
        try:
            f = open(self.blacklist_file, "r")
            for line in f.readlines():
                self.blacklist[line.strip()] = 0
            f.close()
        except FileNotFoundError:
            pass

    def save_blacklist(self):
        f = open(self.blacklist_file, "w")
        for key in self.blacklist:
            if self.blacklist[key] == 1:
                f.write("{0}\n".format(key))
        f.close()

    def find_containers(self):
        self.load_blacklist()

        ps = os.popen("docker ps")
        for line in ps.readlines():
            match = re.match("([0-9a-f]+)\s+(\S+)", line)
            if match:
                container = match.group(1)
                image = match.group(2)

                ipx = os.popen("docker exec {0} ip -o -f inet addr show eth0"
                               .format(container))
                ip = None
                for line in ipx.readlines():
                    match = re.match("\d+:\s+eth0\s+inet\s+([0-9.]+)", line)
                    if match:
                        ip = match.group(1)
                if ip is None:
                    print("Cannot read IP address of container {0}"
                          .format(container))
                else:
                    self.ipaddr[container] = ip

                if container in self.blacklist:
                    self.blacklist[container] = 1
                    self.container_list.append(container)
                    self.containers[container] = image
                else:
                    if re.match(self.imatch, image):
                        self.container_list.append(container)
                        self.containers[container] = image

    def display_info(self):
        # Display information about docker containers
        if self.count is None:
            dcount = 100000 # hack
        else:
            dcount = self.count

        # Sigh. Report formatting is such a drag...
        dinfo = []
        ps = os.popen("docker ps")
        for line in ps.readlines():
            match = re.match("([0-9a-f]+)\s+(\S+)", line)
            if match:
                container = match.group(1)
                image = match.group(2)
                ip = self.ipaddr[container]
                attr = []
                if container in self.blacklist:
                    attr.append("used")
                else:
                    if dcount <= 0:
                        attr.append("skip")
                    else:
                        if re.match(self.imatch, image):
                            dcount -= 1
                            attr.append("*")
                            if container == self.bootimage:
                                attr.append("boot")
                        else:
                            attr.append("!~"+self.imatch)

                data = {"container": container,
                        "image": image,
                        "ipaddr": ip,
                        "flags": ", ".join(attr)}
                dinfo.append(data)

        headers = {"container": "Container",
                   "image": "Image",
                   "ipaddr": "IP Addr",
                   "flags": "Flags"}

        maxlen = {}
        for key in dinfo[0]:
            flen = len(headers[key])
            for data in dinfo:
                if len(data[key]) > flen:
                    flen = len(data[key])
            maxlen[key] = flen

        fstr = "%-{0}s  %-{1}s  %-{2}s  %s".format(
            maxlen['container'], maxlen['image'], maxlen['ipaddr'])

        print(fstr % (headers['container'], headers['image'],
                      headers['ipaddr'], headers['flags']))

        for data in dinfo:
            print(fstr % (data['container'], data['image'],
                          data['ipaddr'], data['flags']))


def main():
    parser = argparse.ArgumentParser(
        description="Configure instances of MarkLogic server " \
                    + "running in Docker containers.")

    parser.add_argument('-u', '--credentials', default='admin:admin',
                        metavar='USER:PASS',
                        help='Admin user:pass for new cluster')
    parser.add_argument('--realm', default='public',
                        help='Security realm for new cluster')
    parser.add_argument('--image', default='ml[0-9]',
                        metavar='IMGREGEX',
                        help='Regex for matching Docker image names')
    parser.add_argument('--boot',
                        metavar='HOST',
                        help='Select the bootstrap host for new cluster')
    parser.add_argument('--maxhosts', type=int,
                        help='Maximum number of containers to cluster')
    parser.add_argument('--name',
                        help='Set the cluster name for the new cluster')
    parser.add_argument('--couple',
                        metavar='BOOTHOST',
                        help='Bootstrap host of cluster with which to couple')
    parser.add_argument('--couple-credentials',
                        metavar='USER:PASS',
                        help='Admin user:pass for cluster with which to couple')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = vars(parser.parse_args())

    docker = Docker()

    for opt in args:
        arg = args[opt]
        if opt == "credentials":
            try:
                adminuser, adminpass = re.split(":", arg)
                docker.set_credentials(adminuser,adminpass)
            except ValueError:
                print ("--credentials value must be 'user:password':", arg)
                sys.exit(1)
        if opt == "realm":
            docker.set_realm(arg)
        if opt == "image":
            docker.set_image_match(arg)
        if opt == "boot":
            docker.set_boot_image(arg)
        if opt == "maxhosts":
            docker.set_count(arg)
        if opt == "name":
            docker.set_name(arg)
        if opt == "couple":
            docker.set_couple(arg)
        if opt == "couple-credentials":
            try:
                adminuser, adminpass = re.split(":", arg)
                docker.set_couple_credentials(adminuser,adminpass)
            except ValueError:
                print ("--couple-credentials value must be 'user:password':", arg)
                sys.exit(1)

    if args['debug']:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("marklogic").setLevel(logging.DEBUG)

    docker.setup_cluster()

if __name__ == '__main__':
  main()
