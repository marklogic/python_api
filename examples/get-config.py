#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script takes a list of server artifacts (databases, servers, users,
# roles, etc.) and computes the "closure" over those artifacts. In other words,
# each artifact is included as well as all of the artifacts that each depends
# on. (A server depends on a database, for example, and may depend on a user
# and a privilege.)
#
# This closure is simply reported to the user or, if the --json option is
# used, returned as a JSON object.
#
# See put-config.py
#
# For example:
#
# python3 get-config --server myapp
#
# or
#
# python3 get-config --json --server myapp > /tmp/config.json
#
# TODO

# * The set of artifacts is incomplete.

__author__ = 'ndw'

import argparse
import logging
import json
import logging
from requests.auth import HTTPDigestAuth
from marklogic.models.connection import Connection
from marklogic.models.database import Database
from marklogic.models.permission import Permission
from marklogic.models.privilege import Privilege
from marklogic.models.role import Role
from marklogic.models.forest import Forest
from marklogic.models.server import Server
from marklogic.models.user import User

class Closure:
    def __init__(self):
        self.databases = {}
        self.forests = {}
        self.servers = {}
        self.users = {}
        self.roles = {}
        self.privileges = {}
        pass

    def dump(self):
        print ("Servers:")
        for item in self.servers:
            print("\t{0}".format(item))

        print ("Databases:")
        for item in self.databases:
            print("\t{0}".format(item))

        print ("Forests:")
        for item in self.forests:
            print("\t{0}".format(item))

        print ("Users:")
        for item in self.users:
            print("\t{0}".format(item))

        print ("Roles:")
        for item in self.roles:
            print("\t{0}".format(item))

        print ("Privileges:")
        for item in self.privileges:
            print("\t{0}".format(item))

    def close(self, conn, group='Default'):
        closed = False
        while not closed:
            closed = True

            newitems = []
            for key in self.servers:
                item = self.servers[key]
                if item is None:
                    closed = False
                    newitems.append(Server.lookup(conn, key, group))

            for server in newitems:
                self._close_over_server(server)

            newitems = []
            for key in self.databases:
                item = self.databases[key]
                if item is None:
                    closed = False
                    newitems.append(Database.lookup(conn, key))

            for database in newitems:
                self._close_over_database(database)

            newitems = []
            for key in self.forests:
                item = self.forests[key]
                if item is None:
                    closed = False
                    newitems.append(Forest.lookup(conn, key))

            for forest in newitems:
                self._close_over_forest(forest)

            newitems = []
            for key in self.users:
                item = self.users[key]
                if item is None:
                    closed = False
                    newitems.append(User.lookup(conn, key))

            for user in newitems:
                self._close_over_user(user)

            newitems = []
            for key in self.roles:
                item = self.roles[key]
                if item is None:
                    closed = False
                    newitems.append(Role.lookup(conn, key))

            for role in newitems:
                self._close_over_role(role)

            delitems = []
            newitems = []
            for key in self.privileges:
                item = self.privileges[key]
                parts = key.split("|")
                kind = parts[0]
                name = parts[1]
                if isinstance(item, str):
                    closed = False
                    if "//" in key:
                        # Assume it's an action
                        priv = Privilege.lookup(conn, action=name, kind=kind)
                        delitems.append(key)
                    else:
                        priv = Privilege.lookup(conn, name, kind)
                    newitems.append(priv)

            for item in delitems:
                del self.privileges[item]

            for priv in newitems:
                self._close_over_privilege(priv)

    def add_server(self, server):
        if (isinstance(server, str)):
            name = server
        else:
            name = server.server_name()

        if name in self.servers and self.servers[name] is not None:
            return

        if (isinstance(server, str)):
            self.servers[name] = None
        else:
            self.servers[name] = server
            self._close_over_server(server)

    def _close_over_server(self, server):
        self.servers[server.server_name()] = server
        for name in [server.content_database_name(),
                     server.last_login_database_name(),
                     server.modules_database_name()]:
            if name is not None:
                    self.add_database(name)

        if server.default_user() is not None:
            self.add_user(server.default_user())

        if server.privilege_name() is not None:
            self.add_privilege(server.privilege_name(), "execute")

    def add_database(self, database):
        if (isinstance(database, str)):
            name = database
        else:
            name = database.database_name()

        if name in self.databases and self.databases[name] is not None:
            return

        if (isinstance(database, str)):
            self.databases[name] = None
        else:
            self.databases[name] = database
            self._close_over_database(self, database)

    def add_forest(self, forest):
        if (isinstance(forest, str)):
            name = forest
        else:
            name = forest.database_name()

        if name in self.forests and self.forests[name] is not None:
            return

        if (isinstance(forest, str)):
            self.forests[name] = None
        else:
            self.forests[name] = forest

    def _close_over_database(self, database):
        self.databases[database.database_name()] = database
        for name in [database.security_database_name(),
                     database.schema_database_name(),
                     database.triggers_database_name()]:
            if name is not None:
                    self.add_database(name)
        for name in database.forest_names():
            self.add_forest(name)

    def _close_over_forest(self, forest):
        forest.set_host("$ML-LOCALHOST")
        forest.set_database(None)
        self.forests[forest.forest_name()] = forest

    def add_user(self, user):
        if (isinstance(user, str)):
            name = user
        else:
            name = user.user_name()

        if name in self.users and self.users[name] is not None:
            return

        self.users[name] = None
        if (not isinstance(user, str)):
            self.users[name] = user
            self._close_over_user(user)

    def _close_over_user(self, user):
        self.users[user.user_name()] = user
        for role in user.role_names():
            self.add_role(role)

        if user.permissions() is not None:
            for perm in user.permissions():
                self.add_role(perm.role_name())

    def add_role(self, role):
        if (isinstance(role, str)):
            name = role
        else:
            name = role.role_name()

        if name in self.roles and self.roles[name] is not None:
            return

        self.roles[name] = None
        if (not isinstance(role, str)):
            self.roles[name] = role
            self._close_over_role(role)

    def _close_over_role(self, role):
        self.roles[role.role_name()] = role
        if role.role_names() is not None:
            for role in role.role_names():
                self.add_role(role)

    def add_privilege(self, privilege, kind):
        if (isinstance(privilege, str)):
            name = privilege
        else:
            name = privilege.privilege_name()

        key = "{0}|{1}".format(kind,name)

        if name in self.privileges:
            if not isinstance(self.privileges[key], str):
                return

        self.privileges[key] = kind
        if (not isinstance(privilege, str)):
            self.privileges[key] = privilege
            self._close_over_privilege(privilege)

    def _close_over_privilege(self, privilege):
        key = "{0}|{1}".format(privilege.kind(),privilege.privilege_name())

        self.privileges[key] = privilege
        for role in privilege.role_names():
            self.add_role(role)

    def marshal(self):
        config = {
            'servers': [],
            'forests': [],
            'databases': [],
            'users': [],
            'roles': [],
            'privileges': []
            }

        for item in self.servers:
            config['servers'].append(self.servers[item].marshal())

        for item in self.databases:
            config['databases'].append(self.databases[item].marshal())

        for item in self.forests:
            config['forests'].append(self.forests[item].marshal())

        for item in self.users:
            config['users'].append(self.users[item].marshal())

        for item in self.roles:
            config['roles'].append(self.roles[item].marshal())

        for item in self.privileges:
            config['privileges'].append(self.privileges[item].marshal())

        return config

#logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--server", action='append',
                    help="Server name, or group|name")
parser.add_argument("--database", action='append',
                    help="Database name")
parser.add_argument("--user", action='append',
                    help="User name")
parser.add_argument("--role", action='append',
                    help="Role name")
parser.add_argument("--execute-privilege", action='append',
                    help="Privilege name")
parser.add_argument("--uri-privilege", action='append',
                    help="Privilege name")
parser.add_argument("--host", action='store', default="localhost",
                    help="Management API host")
parser.add_argument("--username", action='store', default="admin",
                    help="User name")
parser.add_argument("--password", action='store', default="admin",
                    help="Password")
parser.add_argument("--json", action="store_true",
                    help="Return the results as JSON")
parser.add_argument('--debug', action='store_true',
                    help='Enable debug logging')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)

closure = Closure()

conn = Connection(args.host, HTTPDigestAuth(args.username, args.password))

if args.server:
    for name in args.server:
        server = Server.lookup(conn, name)
        closure.add_server(server)

if args.database:
    for name in args.database:
        database = Database.lookup(conn, name)
        closure.add_database(database)

if args.user:
    for name in args.user:
        user = User.lookup(conn, name)
        closure.add_user(user)

if args.role:
    for name in args.role:
        role = Role.lookup(conn, name)
        closure.add_role(server)

if args.execute_privilege:
    for name in args.execute_privilege:
        closure.add_privilege(name, "execute")

if args.uri_privilege:
    for name in args.uri_privilege:
        closure.add_privilege(name, "uri")

closure.close(conn)

if args.json:
    print(json.dumps(closure.marshal()))
else:
    closure.dump()
