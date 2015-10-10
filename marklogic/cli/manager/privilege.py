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
A class to manage privileges.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.privilege import Privilege

class PrivilegeManager(Manager):
    """
    The PrivilegeManager performs operations on privileges.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        ptype = args['kind']
        names = Privilege.list(connection, kind=ptype)
        print(json.dumps(names,sort_keys=True, indent=2))

    def create(self, args, config, connection):
        privilege = Privilege(args['name'], args['kind'], action=args['action'],
                              connection=connection)
        if privilege.exists():
            print("Error: Privilege already exists: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            newpriv = self._read(args['name'], args['json'])
            newpriv.connection = privilege.connection
            privilege = newpriv

        self.roles = []
        self._properties(privilege, args)
        if len(self.roles) > 0:
            privilege.set_role_names(self.roles)

        print("Create privilege {0}...".format(args['name']))
        privilege.create(connection)

    def modify(self, args, config, connection):
        privilege = Privilege(args['name'], args['kind'], connection=connection)
        if not privilege.exists():
            print("Error: Privilege does not exist: {0}".format(args['name']))
            sys.exit(1)

        privilege.read()

        if args['json'] is not None:
            newpriv = self._read(args['name'], args['json'])
            newpriv.connection = privilege.connection
            privilege = newpriv

        self.roles = []
        self._properties(privilege, args)
        if len(self.roles) > 0:
            privilege.set_role_names(self.roles)

        print("Modify privilege {0}...".format(args['name']))
        privilege.update(connection=connection)

    def delete(self, args, config, connection):
        privilege = Privilege.lookup(connection,
                                     name=args['name'],
                                     kind=args['kind'])
        if privilege is None:
            return

        print("Delete privilege {0}...".format(args['name']))
        privilege.delete(connection)

    def get(self, args, config, connection):
        privilege = Privilege(args['name'], args['kind'], connection=connection)
        if not privilege.exists():
            print("Error: Privilege does not exist: {0}".format(args['name']))
            sys.exit(1)

        privilege.read()
        self.jprint(privilege)

    def _special_property(self, name, value):
        if name == 'role':
            self.roles.append(value)
        else:
            super()._special_property(name,value)

    def _read(self, name, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['privilege-name'] = name
        privilege = Privilege.unmarshal(data)
        return privilege
