#!/usr/bin/python3

import sys
import re
import os
import pwd
import logging
import argparse
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
from marklogic.models.host import Host
from marklogic.connection import Connection
from marklogic.exceptions import *

class Docker:
    def __init__(self):
        self.marklogic = None
        self.uname = pwd.getpwuid(os.getuid()).pw_name
        self.adminuser = "admin"
        self.adminpass = "admin"
        self.realm = "public"
        self.imatch = "ml[0-9]"
        self.bootimage = None
        self.localimage = False
        self.count = None
        self.couple = None
        self.couple_user = None
        self.couple_pass = None
        self.name = None
        self.blacklist_file = "/tmp/{0}.docker.skip".format(self.uname)
        self.blacklist = {}
        self.container_list = []
        self.cluster_list = []
        self.containers = {}
        self.localip = None
        self.ipaddr = {}
        self.hostname = {}

    def set_credentials(self, user, password):
        self.adminuser = user
        self.adminpass = password

    def set_realm(self, realm):
        self.realm = realm

    def set_image_match(self, match):
        self.imatch = match

    def set_boot_image(self, image):
        self.bootimage = image
        self.localimage = (image == "localhost")

    def set_count(self, count):
        self.count = count

    def set_couple(self, couple):
        self.couple = couple

    def set_couple_credentials(self, user, password):
        self.couple_user = user
        self.couple_pass = password

    def set_name(self, name):
        self.name = name

    def setup_cluster(self):
        if self.couple is not None and self.couple_pass is None:
            self.couple_pass = self.adminpass
            self.couple_user = self.adminuser

        self.load_blacklist()
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
            self.bootimage = self.pick_image(self.bootimage)
            if self.bootimage in self.container_list:
                self.container_list.remove(self.bootimage)

        self.cluster_list = self.pick_containers()

        self.display_info()
        #sys.exit(1)

        # Initialize the bootstrap image, if necessary

        if self.localimage:
            bootip = self.localip
        else:
            bootip = self.ipaddr[self.bootimage]

        if self.ml_init(bootip, self.bootimage):
            self.ml_security(bootip, self.bootimage)

        conn = Connection(bootip, HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        for container in self.cluster_list:
            if container == self.bootimage:
                continue
            ip = self.ipaddr[container]
            self.ml_init(ip, container)
            self.ml_join(bootip, ip)

        if self.name is not None:
            print("{0}: rename cluster...".format(bootip))
            cluster = self.marklogic.cluster()
            cluster.set_cluster_name(self.name)
            cluster.update()

        if self.couple is not None:
            for couple in self.couple:
                print("{0}: couple with {1}...".format(bootip, couple))
                altconn = Connection(couple,
                                     HTTPDigestAuth(self.couple_user,
                                                    self.couple_pass))
                altml = MarkLogic(altconn)
                altcluster = altml.cluster()
                cluster = self.marklogic.cluster()
                cluster.couple(altcluster)

        print("Finished")

    def ml_init(self, ip, container):
        if container in self.hostname:
            hostname = self.hostname[container]
        else:
            hostname = container
        print("{0}: initialize host {1}...".format(ip, hostname))
        try:
            host = MarkLogic.instance_init(ip)
        except UnauthorizedAPIRequest:
            # Assume that this happened because the host is already initialized
            host = Host(ip)

        self.blacklist[container] = "used"
        self.save_blacklist()
        return host.just_initialized()

    def ml_join(self, bootip, ip):
        print("{0}: join cluster with {1}...".format(ip, bootip))
        cluster = self.marklogic.cluster()
        host = Host(ip)
        cluster.add_host(host)

    def ml_security(self, ip, container):
        print("{0}: initialize security...".format(ip))
        MarkLogic.instance_admin(ip, self.realm, self.adminuser, self.adminpass)
        self.blacklist[container] = "boot"
        self.save_blacklist()

    def pick_image(self, name):
        if name is None:
            for container in self.container_list:
                if not container in self.blacklist:
                    return container
            print("Cannot find unused container")
            sys.exit(1)

        for key in self.hostname:
            if name == self.hostname[key]:
                return key

        count = 0
        container = None
        for key in self.ipaddr:
            if name == self.ipaddr[key]:
                return key
            if re.match("^"+name, key):
                count += 1
                container = key
        if count == 1:
            return container
        if count > 1:
            print("Ambiguous container id:", name)
            sys.exit(1)

        for key in self.containers:
            image = self.containers[key]
            if (key == self.bootimage or re.match(self.bootimage, image)):
                return key

        print("Cannot find container \"{0}\".".format(name))
        sys.exit(1)

    def pick_containers(self):
        if self.count is None:
            count = -1
        else:
            count = self.count - 1

        cset = set()

        if not self.localimage:
            cset.add(self.bootimage)

        for container in self.container_list:
            if container == self.bootimage or container in self.blacklist:
                continue
            if count == 0:
                continue
            cset.add(container)
            count -= 1

        containers = []
        for key in cset:
            containers.append(key)
        return containers

    def load_blacklist(self):
        try:
            f = open(self.blacklist_file, "r")
            for line in f.readlines():
                (container, flag) = line.strip().split(" ")
                self.blacklist[container] = flag
            f.close()
        except FileNotFoundError:
            pass

    def save_blacklist(self):
        f = open(self.blacklist_file, "w")
        for key in self.blacklist:
            if self.blacklist[key] != "gone":
                f.write("{0} {1}\n".format(key, self.blacklist[key]))
        f.close()

    def find_containers(self):
        self.load_blacklist()

        ps = os.popen("docker ps")
        for line in ps.readlines():
            match = re.match("([0-9a-f]+)\s+(\S+)", line)
            if match:
                container = match.group(1)
                image = match.group(2)

                ipx = os.popen("docker inspect {0}".format(container))
                ip = None
                hostname = None
                for line in ipx.readlines():
                    match = re.match('\s+"IPAddress": "([^"]+)"', line)
                    if match:
                        ip = match.group(1)
                    match = re.match('\s+"Hostname": "([^"]+)"', line)
                    if match:
                        hostname = match.group(1)
                if ip is None:
                    print("Cannot read IP address of container {0}"
                          .format(container))
                else:
                    self.ipaddr[container] = ip

                if hostname is None:
                    print("Cannot read hostname of container {0}"
                          .format(container))
                else:
                    self.hostname[container] = hostname

                if re.match(self.imatch, image):
                    self.container_list = [container] + self.container_list
                    self.containers[container] = image

        for container in self.blacklist:
            if not container in self.containers:
                self.blacklist[container] = "gone"

    def display_info(self):
        # Display information about docker containers
        # Sigh. Report formatting is such a drag...
        dinfo = []
        ps = os.popen("docker ps")
        for line in ps.readlines():
            match = re.match("([0-9a-f]+)\s+(\S+)", line)
            if match:
                container = match.group(1)
                image = match.group(2)
                ip = self.ipaddr[container]
                hostname = self.hostname[container]
                attr = []
                if container in self.blacklist:
                    attr.append("used")
                    if self.blacklist[container] == "boot":
                        attr.append("boot")
                else:
                    if not container in self.cluster_list:
                        attr.append("skip")
                    else:
                        if re.match(self.imatch, image):
                            attr.append("*")
                            if container == self.bootimage:
                                attr.append("boot")
                        else:
                            attr.append("!~"+self.imatch)

                data = {"container": container,
                        "image": image,
                        "ipaddr": ip,
                        "hostname": hostname,
                        "flags": ", ".join(attr)}
                dinfo = [data] + dinfo

        headers = {"container": "Container",
                   "image": "Image",
                   "hostname": "Hostname",
                   "ipaddr": "IP Addr",
                   "flags": "Flags"}

        maxlen = {}
        for key in dinfo[0]:
            flen = len(headers[key])
            for data in dinfo:
                if len(data[key]) > flen:
                    flen = len(data[key])
            maxlen[key] = flen

        fstr = "%-{0}s  %-{1}s  %-{2}s  %-{3}s  %s".format(
            maxlen['container'], maxlen['image'],
            maxlen['hostname'], maxlen['ipaddr'])

        print(fstr % (headers['container'], headers['image'],
                      headers['hostname'], headers['ipaddr'],
                      headers['flags']))

        for data in dinfo:
            print(fstr % (data['container'], data['image'],
                          data['hostname'], data['ipaddr'], data['flags']))


def main():
    parser = argparse.ArgumentParser(
        description="Configure instances of MarkLogic server " \
                    + "running in Docker containers.")

    parser.add_argument('--credentials', default='admin:admin',
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
    parser.add_argument('--couple', nargs="+",
                        metavar='BOOTHOST(S)',
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
        if opt == "credentials" and arg is not None:
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
        if opt == "couple_credentials" and arg is not None:
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
