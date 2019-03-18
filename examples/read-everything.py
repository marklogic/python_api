#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script attempts to read all of the resource types on the cluster.
# The point of this script is to make sure that we catch any new properties
# that have been added by the server.

__author__ = 'ndw'

import argparse
import logging
import json
import logging
import sys
from requests.auth import HTTPDigestAuth
from marklogic.connection import Connection
from marklogic.models.cluster import LocalCluster
from marklogic.models.group import Group
from marklogic.models.host import Host
from marklogic.models.database import Database
from marklogic.models.permission import Permission
from marklogic.models.privilege import Privilege
from marklogic.models.role import Role
from marklogic.models.forest import Forest
from marklogic.models.server import Server
from marklogic.models.user import User

class ReadEverything:
    def __init__(self, connection):
        self.databases = {}
        self.forests = {}
        self.servers = {}
        self.users = {}
        self.roles = {}
        self.privileges = {}
        self.connection = connection
        pass

    def readClass(self, kind, klass, max_read=sys.maxsize):
        names = klass.list(self.connection)
        for name in names:
            if max_read > 0:
                if name.find("|") > 0:
                    parts = name.split("|")
                    rsrc = klass.lookup(self.connection, parts[0], parts[1])
                else:
                    rsrc = klass.lookup(self.connection, name)
                max_read = max_read - 1
        print("{}: {}".format(kind, len(names)))

    def readPrivileges(self):
        names = Privilege.list(self.connection)
        max_read = { "execute": 5, "uri": 5 }
        counts = { "execute": 0, "uri": 0 }
        for name in names:
            parts = name.split("|")
            kind = parts[0]
            pname = parts[1]

            counts[kind] = counts[kind] + 1

            if max_read[kind] > 0:
                rsrc = Privilege.lookup(self.connection, pname, kind)
                max_read[kind] = max_read[kind] - 1

        print("Execute privileges: {}".format(counts["execute"]))
        print("URI privileges: {}".format(counts["uri"]))

    def read(self):
        conn = self.connection
        cluster = LocalCluster(connection=conn).read()
        print("Read local cluster: {}".format(cluster.cluster_name()))

        x = cluster.security_version()
        x = cluster.effective_version()
        x = cluster.cluster_id()
        x = cluster.cluster_name()
        x = cluster.ssl_fips_enabled()
        x = cluster.xdqp_ssl_certificate()
        x = cluster.xdqp_ssl_private_key()
        x = cluster.bootstrap_hosts()
        # FIXME:
        #x = cluster.foreign_cluster_id()
        #x = cluster.foreign_cluster_name()
        x = cluster.language_baseline()
        x = cluster.opsdirector_log_level()
        x = cluster.opsdirector_metering()
        x = cluster.opsdirector_session_endpoint()

        self.readClass("Groups", Group, max_read=5)
        self.readClass("Hosts", Host, max_read=5)
        self.readClass("Databases", Database, max_read=5)
        self.readClass("Forests", Forest, max_read=5)
        self.readClass("Servers", Server)
        self.readClass("Roles", Role, max_read=5)
        self.readClass("Users", User, max_read=5)
        self.readPrivileges()

        return

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--host", action='store', default="localhost",
                    help="Management API host")
parser.add_argument("--username", action='store', default="admin",
                    help="User name")
parser.add_argument("--password", action='store', default="admin",
                    help="Password")
parser.add_argument('--debug', action='store_true',
                    help='Enable debug logging')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)

conn = Connection(args.host, HTTPDigestAuth(args.username, args.password))
read_everything = ReadEverything(conn)

print("Reading all resources from {}".format(args.host))

read_everything.read()

print("Finished")
