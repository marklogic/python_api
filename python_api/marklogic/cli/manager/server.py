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

    def list(self, args, config, connection):
        stype = args['type']
        if stype == None:
            slist = Server.list(connection)
        elif stype == 'http':
            slist = HttpServer.list(connection)
        elif stype == 'odbc':
            slist = OdbcServer.list(connection)
        elif stype == 'xdbc':
            slist = XdbcServer.list(connection)
        elif stype == 'webdav':
            slist = WebDAVServer.list(connection)
        else:
            print("Unexpected server type: {0}".format(stype))
            sys.exit(1)

        names = []
        for key in slist:
            (group,name) = key.split('|')
            if group == args['group']:
                names.append(name)

        print(json.dumps(names,sort_keys=True, indent=2))

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

        if args['json'] is not None:
            server = self._read(args['name'], args['group'], stype, args['json'])

        self._properties(server, args)

        server.create()

    def modify(self, args, config, connection):
        server = Server.lookup(connection, args['name'], args['group'])
        if server is None:
            print("Error: Server does not exist: {0} in group {1}"
                  .format(args['name'], args['group']))
            sys.exit(1)

        if args['json'] is not None:
            server = self._read(args['name'], args['group'],
                                server.server_type(), args['json'])

        self._properties(server, args)

        print("Modify server {0} in group {1}..."
              .format(args['name'], args['group']))
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

    def get(self, args, config, connection):
        server = Server.lookup(connection, args['name'], args['group'])
        if server is None:
            print("Error: Server does not exist: {0} in group {1}"
                  .format(args['name'], args['group']))
            sys.exit(1)
        self.jprint(server)

    def _read(self, name, group, stype, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['server-name'] = name
        data['group-name'] = group
        data['server-type'] = stype

        if stype == 'http':
            server = HttpServer(name, group)
        elif stype == 'odbc':
            server = OdbcServer(name, group)
        elif stype == 'xdbc':
            server = XdbcServer(name, group)
        elif stype == 'webdav':
            server = WebDAVServer(name, group)
        else:
            print("Unexpected server type: {0}".format(stype))
            sys.exit(1)

        server = server.unmarshal(data)
        return server
