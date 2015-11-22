#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script takes a JSON object that enumerates a set of artifacts and
# removes those artifacts from the server.
#
# See put-config.py
#
# For example:
#
# python3 delete-config --json /tmp/config.json
#
# TODO
#

__author__ = 'pmb'

import argparse
import logging
import json
import os
import base64
import logging
from requests.auth import HTTPDigestAuth
from marklogic.connection import Connection
from marklogic.models.database import Database
from marklogic.models.forest import Forest
from marklogic.models.permission import Permission
from marklogic.models.privilege import Privilege
from marklogic.models.role import Role
from marklogic.models.server import Server
from marklogic.models.user import User

#logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--host", action='store', default="localhost",
                    help="Management API host")
parser.add_argument("--username", action='store', default="admin",
                    help="User name")
parser.add_argument("--password", action='store', default="admin",
                    help="Password")
parser.add_argument("--json", action="store",
                    help="Name of the file containing JSON config")
parser.add_argument('--debug', action='store_true',
                    help='Enable debug logging')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)

with open(args.json) as data_file:
    data = json.load(data_file)

conn = Connection(args.host, HTTPDigestAuth(args.username, args.password))

# Delete users
for config in data['users']:
    name = config['user-name']
    user = User.lookup(conn, name)
    if user is not None:
        verb = "Deleting"
        user = User.unmarshal(config)
        print("{0} user: {1}".format(verb, name))
        user.delete(conn)

# Delete privileges
for config in data['privileges']:
    name = config['privilege-name']
    kind = config['kind']
    priv = Privilege.lookup(conn, name, kind)
    if priv is not None:
        verb = "Deleting"
        priv = Privilege.unmarshal(config)
        print("{0} {1} privilege: {2}".format(verb, kind, name))
        priv.delete(conn)

# Delete roles
for config in data['roles']:
    name = config['role-name']
    role = Role.lookup(conn, name)
    if role is not None:
        print("Deleting role: {0}".format(name))
        role = Role(name)
        role.delete(conn)

# Delete servers
for config in data['servers']:
    name = config['server-name']
    group = config['group-name']
    server = Server.lookup(conn, name, group)
    if server is not None:
        verb = "Deleting"
        server = Server.unmarshal(config)
        kind = server.server_type()
        print("{0} {1} server: {2}".format(verb, kind, name))
        server.delete(conn)

# Delete databases
for config in data['databases']:
    name = config['database-name']
    db = Database.lookup(conn, name)
    if db is not None:
        print("Deleting database: {0}".format(name))
        db.delete(connection=conn)

# Delete forests
for config in data['forests']:
    name = config['forest-name']
    f = Forest.lookup(conn, name)
    if f is not None:
        print("Deleting forest: {0}".format(name))
        f.delete(connection=conn)
