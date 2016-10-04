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

"""
This app joins several MarkLogic instances together into a cluster.
It can also couple that cluster to another existing cluster.
"""

class App:
    def __init__(self):
        self.marklogic = None
        self.uname = pwd.getpwuid(os.getuid()).pw_name
        self.adminuser = "admin"
        self.adminpass = "admin"
        self.realm = "public"
        self.host = None
        self.boothost = None
        self.couple = None
        self.couple_user = None
        self.couple_pass = None
        self.name = None

    def set_credentials(self, user, password):
        self.adminuser = user
        self.adminpass = password

    def set_realm(self, realm):
        self.realm = realm

    def set_boot_host(self, host):
        self.boothost = host

    def set_host(self, name):
        self.host = name

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

        if self.boothost is None:
            self.boothost = self.host[0]
            self.host.remove(self.boothost)

        if self.ml_init(self.boothost):
            self.ml_security(self.boothost)

        conn = Connection(self.boothost, HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        for hostname in self.host:
            self.ml_init(hostname)
            self.ml_join(self.boothost, hostname)

        if self.name is not None:
            print("{0}: rename cluster...".format(self.boothost))
            cluster = self.marklogic.cluster()
            cluster.set_cluster_name(self.name)
            cluster.update()

        if self.couple is not None:
            for couple in self.couple:
                print("{0}: couple with {1}...".format(self.boothost, couple))
                altconn = Connection(couple,
                                     HTTPDigestAuth(self.couple_user,
                                                    self.couple_pass))
                altml = MarkLogic(altconn)
                altcluster = altml.cluster()
                cluster = self.marklogic.cluster()
                cluster.couple(altcluster)

        print("Finished")

    def ml_init(self, hostname):
        print("{0}: initialize host...".format(hostname))
        try:
            host = MarkLogic.instance_init(hostname)
        except UnauthorizedAPIRequest:
            # Assume that this happened because the host is already initialized
            host = Host(hostname)

        return host.just_initialized()

    def ml_join(self, boothost, hostname):
        print("{0}: join cluster with {1}...".format(hostname, boothost))
        cluster = self.marklogic.cluster()
        host = Host(hostname)
        cluster.add_host(host)

    def ml_security(self, hostname):
        print("{0}: initialize security...".format(hostname))
        MarkLogic.instance_admin(hostname, self.realm, self.adminuser, self.adminpass)

def main():
    parser = argparse.ArgumentParser(
        description="Join MarkLogic server instances into a cluster")

    parser.add_argument('--credentials', default='admin:admin',
                        metavar='USER:PASS',
                        help='Admin user:pass for new cluster')
    parser.add_argument('--realm', default='public',
                        help='Security realm for new cluster')
    parser.add_argument('--host', nargs="+",
                        metavar='HOST',
                        required=True,
                        help='Hostnames of instances to join')
    parser.add_argument('--boot',
                        metavar='HOST',
                        help='Select the bootstrap host for new cluster')
    parser.add_argument('--name',
                        help='Set the cluster name for the new cluster')
    parser.add_argument('--couple', nargs="+",
                        metavar='BOOTHOST',
                        help='Bootstrap host of cluster with which to couple')
    parser.add_argument('--couple-credentials',
                        metavar='USER:PASS',
                        help='Admin user:pass for cluster with which to couple')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = vars(parser.parse_args())

    app = App()

    for opt in args:
        arg = args[opt]
        if opt == "credentials" and arg is not None:
            try:
                adminuser, adminpass = re.split(":", arg)
                app.set_credentials(adminuser, adminpass)
            except ValueError:
                print ("--credentials value must be 'user:password':", arg)
                sys.exit(1)
        if opt == "realm":
            app.set_realm(arg)
        if opt == "boot":
            app.set_boot_host(arg)
        if opt == "host":
            app.set_host(arg)
        if opt == "name":
            app.set_name(arg)
        if opt == "couple":
            app.set_couple(arg)
        if opt == "couple_credentials" and arg is not None:
            try:
                adminuser, adminpass = re.split(":", arg)
                app.set_couple_credentials(adminuser, adminpass)
            except ValueError:
                print ("--couple-credentials value must be 'user:password':", arg)
                sys.exit(1)

    if args['debug']:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("marklogic").setLevel(logging.DEBUG)

    app.setup_cluster()

if __name__ == '__main__':
  main()
