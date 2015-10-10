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
A class to manage roles.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.role import Role

class RoleManager(Manager):
    """
    The RoleManager performs operations on roles.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        names = Role.list(connection)
        print(json.dumps(names,sort_keys=True, indent=2))

    def create(self, args, config, connection):
        role = Role(args['name'], connection=connection)
        if role.exists():
            print("Error: Role already exists: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            newrole = self._read(args['name'], args['json'])
            newrole.connection = role.connection
            role = newrole

        self.roles = []
        self._properties(role, args)
        if len(self.roles) > 0:
            role.set_role_names(self.roles)

        print("Create role {0}...".format(args['name']))
        role.create(connection)

    def modify(self, args, config, connection):
        role = Role(args['name'], connection=connection)
        if not role.exists():
            print("Error: Role does not exist: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            newrole = self._read(args['name'], args['json'])
            newrole.connection = role.connection
            role = newrole

        self.roles = []
        self._properties(role, args)
        if len(self.roles) > 0:
            role.set_role_names(self.roles)

        print("Modify role {0}...".format(args['name']))
        role.update(connection=connection)

    def delete(self, args, config, connection):
        role = Role.lookup(connection, args['name'])
        if role is None:
            return

        print("Delete role {0}...".format(args['name']))
        role.delete(connection)

    def get(self, args, config, connection):
        role = Role(args['name'], connection=connection)
        if not role.exists():
            print("Error: Role does not exist: {0}".format(args['name']))
            sys.exit(1)

        role.read()
        self.jprint(role)

    def _special_property(self, name, value):
        if name == 'role':
            self.roles.append(value)
        else:
            super()._special_property(name,value)

    def _read(self, name, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['role-name'] = name
        role = Role.unmarshal(data)
        return role
