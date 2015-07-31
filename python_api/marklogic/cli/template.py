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
# Norman Walsh      29 July 2015   Initial development
#

import argparse
from marklogic.cli.manager.forest import ForestManager
from marklogic.cli.manager.database import DatabaseManager
from marklogic.cli.manager.server import ServerManager
from marklogic.cli.manager.user import UserManager

"""
Templates for the command line interface.
"""
class Template:
    """
    The Template class contains the templates for building the
    command line options.
    """
    def __init__(self):
        f_mgr = ForestManager()
        db_mgr = DatabaseManager()
        srv_mgr = ServerManager()
        user_mgr = UserManager()

        self._parsers = {'create': {'forest':   {'code': f_mgr.create},
                                    'database': {'code': db_mgr.create},
                                    'server':   {'code': srv_mgr.create},
                                    'user':     {'code': user_mgr.create}},
                         'delete': {'forest':   {'code': f_mgr.delete},
                                    'database': {'code': db_mgr.delete},
                                    'server':   {'code': srv_mgr.delete},
                                    'user':     {'code': user_mgr.delete}}}

        parser = self._make_parser('create','forest','Create a forest')
        parser.add_argument('name',
                            help='The forest name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to create the forest')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional forest properties')
        self._parsers["create"]["forest"]["parser"] = parser

        parser = self._make_parser('create','database','Create a database')
        parser.add_argument('name',
                            help='The database name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to create forests')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional database properties')
        self._parsers["create"]["database"]["parser"] = parser

        parser = self._make_parser('create','server','Create an application server')
        parser.add_argument('name',
                            help='The server name')
        parser.add_argument('--type', choices=['http','odbc','xdbc','webdav'],
                            default='http',
                            help='The type of server')
        parser.add_argument('--group', default="Default",
                            help='The group')
        parser.add_argument('--port', type=int, required=True,
                            help='The port number')
        parser.add_argument('--root', required=True,
                            help='The root path')
        parser.add_argument('--database', required=True,
                            help='The content database')
        parser.add_argument('--modules', default=None,
                            help='The modules database')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional server properties')
        self._parsers["create"]["server"]["parser"] = parser

        parser = self._make_parser('create','user','Create a user')
        parser.add_argument('name',
                            help='The user name')
        parser.add_argument('--password', required=True,
                            help='The user password')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional user properties')
        self._parsers["create"]["user"]["parser"] = parser

        parser = self._make_parser('delete','forest','Delete a forest')
        parser.add_argument('name',
                            help='The forest name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to create the forest')
        parser.add_argument('--level', choices=['full','config-only'],
                            default='full',
                            help='Level of deletion')
        parser.add_argument('--replicas', choices=['detach','delete'],
                            default='detach',
                            help='Processing for attached replicas')
        self._parsers["delete"]["forest"]["parser"] = parser

        parser = self._make_parser('delete','database','Delete a database')
        parser.add_argument('name',
                            help='The database name')
        parser.add_argument('--forest-delete', choices=['data','configuration'],
                            default='data',
                            help='How to delete attached forests')
        self._parsers["delete"]["database"]["parser"] = parser

        parser = self._make_parser('delete','server','Delete a server')
        parser.add_argument('name',
                            help='The server name')
        parser.add_argument('--group', default="Default",
                            help='The group')
        parser.add_argument('--type', choices=['http','odbc','xdbc','webdav'],
                            help='The type of server')
        self._parsers["delete"]["server"]["parser"] = parser

        parser = self._make_parser('delete','user','Delete a user')
        parser.add_argument('name',
                            help='The user name')
        self._parsers["delete"]["user"]["parser"] = parser

    def _make_parser(self, command, artifact, description=""):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(command, choices=[command], metavar=command,
                            help="The {0} command name".format(command))
        parser.add_argument(artifact, choices=artifact, metavar=artifact,
                            help="The {0} artifact name".format(artifact))
        parser.add_argument('--host', default='localhost',
                            help='Host on which to issue the request')
        parser.add_argument('--credentials', default='admin:admin',
                            help='Login credentials for request')
        parser.add_argument('--debug', action='store_true',
                            help='Enable debug logging')
        return parser

    def command_template(self,command):
        if command in self._parsers:
            return self._parsers[command]
        else:
            None
