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
from marklogic.cli.manager.database import DatabaseManager
from marklogic.cli.manager.forest import ForestManager
from marklogic.cli.manager.marklogic import MarkLogicManager
from marklogic.cli.manager.role import RoleManager
from marklogic.cli.manager.server import ServerManager
from marklogic.cli.manager.user import UserManager
from marklogic.cli.manager.group import GroupManager

"""
Templates for the command line interface.
"""
class Template:
    """
    The Template class contains the templates for building the
    command line options.
    """
    def __init__(self):
        db_mgr = DatabaseManager()
        f_mgr = ForestManager()
        ml_mgr = MarkLogicManager()
        role_mgr = RoleManager()
        srv_mgr = ServerManager()
        user_mgr = UserManager()
        g_mgr = GroupManager()

        self._parsers = {'start':                {'code': ml_mgr.start},
                         'status':               {'code': ml_mgr.status},
                         'init':                 {'code': ml_mgr.init},
                         'save':                 {'code': ml_mgr.save},
                         'switch':               {'code': ml_mgr.switch},
                         'clear':                {'code': ml_mgr.clear},
                         'log':                  {'code': ml_mgr.log},
                         'run':                  {'code': None},
                         'stop':    {'host':     {'code': ml_mgr.stop},
                                     'cluster':  {'code': ml_mgr.stop}},
                         'restart': {'host':     {'code': ml_mgr.restart},
                                     'cluster':  {'code': ml_mgr.restart}},
                         'get':     {'forest':   {'code': f_mgr.get},
                                     'database': {'code': db_mgr.get},
                                     'group':    {'code': g_mgr.get},
                                     'server':   {'code': srv_mgr.get},
                                     'user':     {'code': user_mgr.get},
                                     'role':     {'code': role_mgr.get}},
                         'create':  {'forest':   {'code': f_mgr.create},
                                     'database': {'code': db_mgr.create},
                                     'group':    {'code': g_mgr.create},
                                     'server':   {'code': srv_mgr.create},
                                     'user':     {'code': user_mgr.create},
                                     'role':     {'code': role_mgr.create}},
                         'list':    {'forests':   {'code': f_mgr.list},
                                     'databases': {'code': db_mgr.list},
                                     'groups':    {'code': g_mgr.list},
                                     'servers':   {'code': srv_mgr.list},
                                     'users':     {'code': user_mgr.list},
                                     'roles':     {'code': role_mgr.list}},
                         'modify':  {'forest':   {'code': f_mgr.modify},
                                     'database': {'code': db_mgr.modify},
                                     'group':    {'code': g_mgr.modify},
                                     'server':   {'code': srv_mgr.modify},
                                     'user':     {'code': user_mgr.modify},
                                     'role':     {'code': role_mgr.modify}},
                         'delete':  {'forest':   {'code': f_mgr.delete},
                                     'database': {'code': db_mgr.delete},
                                     'group':    {'code': g_mgr.delete},
                                     'server':   {'code': srv_mgr.delete},
                                     'user':     {'code': user_mgr.delete},
                                     'role':     {'code': role_mgr.delete}}}

        parser = self._make_parser('start',None,'Start the server')
        self._parsers['start']['parser'] = parser

        parser = self._make_parser('status',None,'Report server status')
        self._parsers['status']['parser'] = parser

        parser = self._make_parser('init',None,'Initialize server')
        parser.add_argument('--realm', default='public',
                            help='The realm')
        self._parsers['init']['parser'] = parser

        parser = self._make_parser('stop','host','Stop the host')
        self._parsers['stop']['host']['parser'] = parser

        parser = self._make_parser('stop','cluster','Stop the cluster')
        self._parsers['stop']['cluster']['parser'] = parser

        parser = self._make_parser('restart','host','Restart the host')
        self._parsers['restart']['host']['parser'] = parser

        parser = self._make_parser('restart','cluster','Restart the cluster')
        self._parsers['restart']['cluster']['parser'] = parser

        parser = self._make_parser('save',None,'Save configuration')
        parser.add_argument('--archive', required=True,
                            help='The name of the archive file')
        self._parsers['save']['parser'] = parser

        parser = self._make_parser('switch',None,'Switch configuration')
        parser.add_argument('--archive', required=True,
                            help='The name of the archive file')
        self._parsers['switch']['parser'] = parser

        parser = self._make_parser('clear',None,'Clear configuration')
        self._parsers['clear']['parser'] = parser

        parser = self._make_parser('log',None,'Show logs')
        parser.add_argument('--logfile', default="ErrorLog.txt",
                            help='The name of the log file')
        self._parsers['log']['parser'] = parser

        parser = self._make_parser('run',None,'Switch configuration')
        parser.add_argument('--script', required=True,
                            help='The name of the script file')
        self._parsers['run']['parser'] = parser

        parser = self._make_parser('create','forest','Create a forest')
        parser.add_argument('name',
                            help='The forest name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to create the forest')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional forest properties')
        self._parsers['create']['forest']['parser'] = parser

        parser = self._make_parser('create','database','Create a database')
        parser.add_argument('name',
                            help='The database name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to create forests')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional database properties')
        self._parsers['create']['database']['parser'] = parser

        parser = self._make_parser('create','group','Create a group')
        parser.add_argument('name',
                            help='The group name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional database properties')
        self._parsers['create']['group']['parser'] = parser

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
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional server properties')
        self._parsers['create']['server']['parser'] = parser

        parser = self._make_parser('create','user','Create a user')
        parser.add_argument('name',
                            help='The user name')
        parser.add_argument('--password', required=True,
                            help='The user password')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional user properties')
        self._parsers['create']['user']['parser'] = parser

        parser = self._make_parser('create','role','Create a role')
        parser.add_argument('name',
                            help='The role name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional user properties')
        self._parsers['create']['role']['parser'] = parser

        parser = self._make_parser('modify','forest','Modify a forest')
        parser.add_argument('name',
                            help='The forest name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional forest properties')
        self._parsers['modify']['forest']['parser'] = parser

        parser = self._make_parser('modify','database','Modify a database')
        parser.add_argument('name',
                            help='The database name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional database properties')
        self._parsers['modify']['database']['parser'] = parser

        parser = self._make_parser('modify','group','Modify a group')
        parser.add_argument('name',
                            help='The group name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional database properties')
        self._parsers['modify']['group']['parser'] = parser

        parser = self._make_parser('modify','server','Modify an application server')
        parser.add_argument('name',
                            help='The server name')
        parser.add_argument('--group', default="Default",
                            help='The group')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional server properties')
        self._parsers['modify']['server']['parser'] = parser

        parser = self._make_parser('modify','user','Modify a user')
        parser.add_argument('name',
                            help='The user name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional user properties')
        self._parsers['modify']['user']['parser'] = parser

        parser = self._make_parser('modify','role','Modify a role')
        parser.add_argument('name',
                            help='The role name')
        parser.add_argument('--json',
                            help='The properties')
        parser.add_argument('properties', nargs="*",
                            metavar="property=value",
                            help='Additional user properties')
        self._parsers['modify']['role']['parser'] = parser

        parser = self._make_parser('list','forests','List forests')
        self._parsers['list']['forests']['parser'] = parser

        parser = self._make_parser('list','databases','List databases')
        self._parsers['list']['databases']['parser'] = parser

        parser = self._make_parser('list','groups','List groups')
        self._parsers['list']['groups']['parser'] = parser

        parser = self._make_parser('list','servers','List application servers')
        parser.add_argument('--group', default="Default",
                            help='The group')
        parser.add_argument('--type', choices=['http','odbc','xdbc','webdav'],
                            help='The type of server')
        self._parsers['list']['servers']['parser'] = parser

        parser = self._make_parser('list','users','List users')
        self._parsers['list']['users']['parser'] = parser

        parser = self._make_parser('list','roles','List roles')
        self._parsers['list']['roles']['parser'] = parser

        parser = self._make_parser('delete','forest','Delete a forest')
        parser.add_argument('name',
                            help='The forest name')
        parser.add_argument('--forest-host', default='$ML-LOCALHOST',
                            help='The host on which to delete the forest')
        parser.add_argument('--level', choices=['full','config-only'],
                            default='full',
                            help='Level of deletion')
        parser.add_argument('--replicas', choices=['detach','delete'],
                            default='detach',
                            help='Processing for attached replicas')
        self._parsers['delete']['forest']['parser'] = parser

        parser = self._make_parser('delete','database','Delete a database')
        parser.add_argument('name',
                            help='The database name')
        parser.add_argument('--forest-delete', choices=['data','configuration'],
                            default='data',
                            help='How to delete attached forests')
        self._parsers['delete']['database']['parser'] = parser

        parser = self._make_parser('delete','group','Delete a group')
        parser.add_argument('name',
                            help='The group name')
        self._parsers['delete']['group']['parser'] = parser

        parser = self._make_parser('delete','server','Delete a server')
        parser.add_argument('name',
                            help='The server name')
        parser.add_argument('--group', default="Default",
                            help='The group')
        parser.add_argument('--type', choices=['http','odbc','xdbc','webdav'],
                            help='The type of server')
        self._parsers['delete']['server']['parser'] = parser

        parser = self._make_parser('delete','user','Delete a user')
        parser.add_argument('name',
                            help='The user name')
        self._parsers['delete']['user']['parser'] = parser

        parser = self._make_parser('delete','role','Delete a role')
        parser.add_argument('name',
                            help='The role name')
        self._parsers['delete']['role']['parser'] = parser

        parser = self._make_parser('get','forest','Get forest properties')
        parser.add_argument('name',
                            help='The forest name')
        self._parsers['get']['forest']['parser'] = parser

        parser = self._make_parser('get','database','Get database properties')
        parser.add_argument('name',
                            help='The database name')
        self._parsers['get']['database']['parser'] = parser

        parser = self._make_parser('get','group','Get group properties')
        parser.add_argument('name', default='Default',
                            help='The group name')
        self._parsers['get']['group']['parser'] = parser

        parser = self._make_parser('get','server','Get server properties')
        parser.add_argument('name',
                            help='The server name')
        parser.add_argument('--group', default="Default",
                            help='The group')
        self._parsers['get']['server']['parser'] = parser

        parser = self._make_parser('get','user','Get user properties')
        parser.add_argument('name',
                            help='The user name')
        self._parsers['get']['user']['parser'] = parser

        parser = self._make_parser('get','role','Get role properties')
        parser.add_argument('name',
                            help='The role name')
        self._parsers['get']['role']['parser'] = parser

    def _make_parser(self, command, artifact, description=""):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(command, choices=[command], metavar=command,
                            help="The {0} command name".format(command))
        if artifact is not None:
            parser.add_argument(artifact, choices=artifact, metavar=artifact,
                                help="The {0} artifact name".format(artifact))
        parser.add_argument('--config', default='DEFAULT',
                            help='Configuration section')
        parser.add_argument('--hostname', default='localhost',
                            help='Host on which to issue the request')
        parser.add_argument('--credentials', default='admin:admin',
                            help='Login credentials for request')
        parser.add_argument('--debug', action='store_true',
                            help='Enable debug logging')
        return parser

    def parsers(self):
        return self._parsers

    def command_template(self,command):
        if command in self._parsers:
            return self._parsers[command]
        else:
            None
