# -*- coding: utf-8 -*-
#
# Copyright 2015 MarkLogic Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# File History
# ------------
#
# Norman Walsh      30 July 2015   Initial development
#

"""
A class to manage servers.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.server import Server, HttpServer, XdbcServer
from marklogic.models.server import OdbcServer, WebDAVServer

class ServerManager(Manager):
    """
    The ServerManager performs operations on servers.
    """
    def __init__(self):
        pass

    def create(self, args, config, connection):
        stype = args['type']
        if stype == 'http':
            server = HttpServer(args['name'], args['group'], args['port'],
                                args['root'], args['database'], args['modules'],
                                connection)
        elif stype == 'odbc':
            server = OdbcServer(args['name'], args['group'], args['port'],
                                args['root'], args['database'], args['modules'],
                                connection)
        elif stype == 'xdbc':
            server = XdbcServer(args['name'], args['group'], args['port'],
                                args['root'], args['database'], args['modules'],
                                connection)
        elif stype == 'webdav':
            server = WebDAVServer(args['name'], args['group'], args['port'],
                                  args['root'], args['database'], connection)
        else:
            print("Unexpected server type: {0}".format(stype))
            sys.exit(1)

        if server.exists(connection):
            print("Error: Server already exists: {0} in group {1}"
                  .format(args['name'], args['group']))
            sys.exit(1)

        if 'properties' in args:
            for prop in args['properties']:
                try:
                    name, value = re.split("=", prop)
                except ValueError:
                    print ("Additional properties must be name=value pairs: {0}"
                           .format(prop))
                    sys.exit(1)
                if value == "false" or value == "true":
                    value = (value == "true")
                else:
                    pass
                print("Unsupported property: {0}".format(prop))
                sys.exit(1)

        server.create()

    def modify(self, args, config, connection):
        server = Server.lookup(connection, args['name'], args['group'])
        if server is None:
            print("Error: Server does not exist: {0} in group {1}"
                  .format(args['name'], args['group']))
            sys.exit(1)

        methods = inspect.getmembers(server, predicate=inspect.ismethod)
        jumptable = {}
        for (name, func) in methods:
            if name.startswith('set_'):
                jumptable[name] = func

        if 'properties' in args:
            for prop in args['properties']:
                try:
                    name, value = re.split("=", prop)
                except ValueError:
                    print ("Additional properties must be name=value pairs: {0}"
                           .format(prop))
                    sys.exit(1)
                if value == "false" or value == "true":
                    value = (value == "true")
                else:
                    pass

                key = "set_" + name.replace("-","_")
                if key in jumptable:
                    jumptable[key](value)
                else:
                    print("Unsupported property: {0}".format(prop))
                    sys.exit(1)

        server.update(connection=connection)

    def delete(self, args, config, connection):
        server = Server.lookup(connection, args['name'], args['group'])
        if server is None:
            return

        if ('type' in args and args['type'] is not None \
            and server.server_type() != args['type']):
            print("Cannot delete {0} in group {1}; server type {2} is not {3}"
                  .format(args['name'], args['group'],
                          server.server_type(), args['type']))
            sys.exit(1)

        server.delete(connection)

