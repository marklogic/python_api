#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script lists all of the artifacts on the server or, if the name (and
# optionally a type) of an artifact is given, displays the properties of
# that artifact.
#
# For example:
#
# python3 properties.py
#
# or
#
# python3 properties.py App-Services
#
# If there's more than one artifact with a given name, you can specify
# the artifact type.
#
# python3 properties.py --forest Documents
#
# TODO
#
# * The set of artifacts is incomplete.

from __future__ import unicode_literals, print_function, absolute_import

import sys
import json
import logging
import argparse
import re
from marklogic.connection import Connection
from marklogic.models.database import Database
from marklogic import MarkLogic
from requests.auth import HTTPDigestAuth
from resources import TestConnection as tc

logging.basicConfig(level=logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("marklogic").setLevel(logging.DEBUG)
logging.getLogger("marklogic.examples").setLevel(logging.INFO)

class Properties:
    def __init__(self):
        self._artifact_types = {'database': 'D',
                                'server': 'S',
                                'host': 'H',
                                'user': 'U',
                                'forest': 'F',
                                'role': 'R'}

    def artifact_types(self):
        return self._artifact_types

    def connect(self, args):
        try:
            adminuser, adminpass = re.split(":", args['credentials'])
        except ValueError:
            print ("--credentials value must be 'user:password':",
                   args['credentials'])
            sys.exit(1)

        if args['debug']:
            logging.basicConfig(level=logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("marklogic").setLevel(logging.DEBUG)

        self.connection \
          = Connection(args['hostname'], HTTPDigestAuth(adminuser, adminpass))
        self.mls = MarkLogic(self.connection)
        self.args = args

    def list_artifacts(self):
        alltypes = True
        artifact_types = self.artifact_types()
        args = self.args
        mls = self.mls

        for atype in artifact_types:
            if args[atype]:
                alltypes = False

        for atype in artifact_types:
            if not alltypes and not args[atype]:
                continue

            if atype == 'database':
                print("Databases:")
                for db in mls.databases():
                    print("\t{0}".format(db))
            elif atype == 'server':
                alist = mls.http_servers()
                if alist:
                    print("HTTP Servers:")
                    for server in alist:
                        print("\t{0}".format(server))
                alist = mls.xdbc_servers()
                if alist:
                    print("XDBC Servers:")
                    for server in alist:
                        print("\t{0}".format(server))
                alist = mls.odbc_servers()
                if alist:
                    print("ODBC Servers:")
                    for server in alist:
                        print("\t{0}".format(server))
                alist = mls.webdav_servers()
                if alist:
                    print("WebDAV Servers:")
                    for server in alist:
                        print("\t{0}".format(server))
            elif atype == 'host':
                alist = mls.hosts()
                if alist:
                    print("Hosts:")
                    for host in alist:
                        print("\t{0}".format(host))
            elif atype == 'user':
                alist = mls.users()
                if alist:
                    print("Users:")
                    for user in alist:
                        print("\t{0}".format(user))
            elif atype == 'forest':
                alist = mls.forests()
                if alist:
                    print("Forests:")
                    for forest in alist:
                        print("\t{0}".format(forest))
            elif atype == 'role':
                alist = mls.roles()
                if alist:
                    print("Roles:")
                    for role in alist:
                        print("\t{0}".format(role))
            else:
                print("Internal error: unexpected artifact type:", atype)


    def show_artifact(self, artifact):
        alltypes = True
        artifact_types = self.artifact_types()
        args = self.args
        mls = self.mls

        for atype in artifact_types:
            if args[atype]:
                alltypes = False

        for atype in artifact_types:
            if not alltypes and not args[atype]:
                continue

            if atype == 'database':
                alist = mls.databases()
                if artifact in alist:
                    prop = mls.database(artifact)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            elif atype == 'server':
                try:
                    servername,groupname = re.split(":", artifact)
                except ValueError:
                    servername = artifact
                    groupname = "Default"

                key = "{0}|{1}".format(groupname, servername)

                alist = mls.http_servers()
                if key in alist:
                    prop = mls.http_server(key)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
                alist = mls.odbc_servers()
                if key in alist:
                    prop = mls.odbc_server(key)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
                alist = mls.xdbc_servers()
                if key in alist:
                    prop = mls.xdbc_server(key)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
                alist = mls.webdav_servers()
                if key in alist:
                    prop = mls.webdav_server(key)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            elif atype == 'host':
                alist = mls.hosts()
                if artifact in alist:
                    prop = mls.host(artifact)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            elif atype == 'user':
                alist = mls.users()
                if artifact in alist:
                    prop = mls.user(artifact)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            elif atype == 'forest':
                alist = mls.forests()
                if artifact in alist:
                    prop = mls.forest(artifact)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            elif atype == 'role':
                alist = mls.roles()
                if artifact in alist:
                    prop = mls.role(artifact)
                    print(json.dumps(prop.marshal()))
                    sys.exit(0)
            else:
                print("Internal error: unexpected artifact type:", atype)

        print("No artifact named:", artifact)

def main():
    props = Properties()

    parser = argparse.ArgumentParser(
        description="Dump MarkLogic server artifact properties.")

    artifact_types = props.artifact_types()

    parser.add_argument('artifact', metavar='artifact-name', nargs="?",
                        help='The name of an artifact (database, server, ...)')
    parser.add_argument('hostname', metavar='host', nargs="?", default='localhost',
                        help='The host to query')
    parser.add_argument('-u', '--credentials', default='admin:admin',
                        metavar='USER:PASS',
                        help='Admin user:pass for new cluster')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging')

    for atype in artifact_types:
        parser.add_argument("-{0}".format(artifact_types[atype]),
                            "--{0}".format(atype),
                            action='store_true',
                            help='Select only ' + atype + ' artifacts')

    args = vars(parser.parse_args())

    props.connect(args)
    if args['artifact'] is None:
        props.list_artifacts()
    else:
        props.show_artifact(args['artifact'])

if __name__ == '__main__':
  main()
