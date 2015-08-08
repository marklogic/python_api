#!/usr/bin/python3

import argparse, json, logging, os, pwd, re, sys
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
from marklogic.models.host import Host
from marklogic.connection import Connection
from marklogic.exceptions import *

class Couple:
    def __init__(self):
        self.marklogic = None
        self.adminuser="admin"
        self.adminpass="admin"
        self.host="localhost"
        self.couple=None
        self.couple_user=None
        self.couple_pass=None

    def set_credentials(self,user,password):
        self.adminuser = user
        self.adminpass = password

    def set_host(self,host):
        self.host = host

    def set_couple(self,couple):
        self.couple = couple

    def set_couple_credentials(self,user,password):
        self.couple_user = user
        self.couple_pass = password

    def couple_cluster(self):
        conn = Connection(self.host, HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        if self.couple is not None:
            for couple in self.couple:
                print("{0}: couple with {1}...".format(self.host,couple))
                altconn = Connection(couple,
                                     HTTPDigestAuth(self.couple_user,
                                                    self.couple_pass))
                altml = MarkLogic(altconn)
                altcluster = altml.cluster()
                cluster = self.marklogic.cluster()
                cluster.couple(altcluster)

        print("Finished")

def main():
    parser = argparse.ArgumentParser(
        description="Couple two clusters")

    parser.add_argument('--credentials', default='admin:admin',
                        metavar='USER:PASS',
                        help='Admin user:pass for cluster')
    parser.add_argument('--host', default='localhost',
                        help='Initial cluster')
    parser.add_argument('--couple', nargs="+",required=True,
                        metavar='BOOTHOST(S)',
                        help='Bootstrap host of cluster with which to couple')
    parser.add_argument('--couple-credentials',default="admin:admin",
                        metavar='USER:PASS',
                        help='Admin user:pass for cluster with which to couple')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = vars(parser.parse_args())

    couple = Couple()

    for opt in args:
        arg = args[opt]
        if opt == "credentials":
            try:
                adminuser, adminpass = re.split(":", arg)
                couple.set_credentials(adminuser,adminpass)
            except ValueError:
                print ("--credentials value must be 'user:password':", arg)
                sys.exit(1)
        if opt == "host":
            couple.set_host(arg)
        if opt == "couple":
            couple.set_couple(arg)
        if opt == "couple_credentials":
            try:
                adminuser, adminpass = re.split(":", arg)
                couple.set_couple_credentials(adminuser,adminpass)
            except ValueError:
                print ("--couple-credentials value must be 'user:password':", arg)
                sys.exit(1)

    if args['debug']:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("marklogic").setLevel(logging.DEBUG)

    couple.couple_cluster()

if __name__ == '__main__':
  main()
