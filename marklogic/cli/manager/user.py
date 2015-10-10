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
A class to manage users.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.user import User

class UserManager(Manager):
    """
    The UserManager performs operations on users.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        names = User.list(connection)
        print(json.dumps(names,sort_keys=True, indent=2))

    def create(self, args, config, connection):
        user = User(args['name'], args['password'], connection=connection)
        if user.exists():
            print("Error: User already exists: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            newuser = self._read(args['name'], args['json'])
            newuser.connection = user.connection
            user = newuser

        self.roles = []
        self._properties(user, args)
        if len(self.roles) > 0:
            user.set_role_names(self.roles)

        print("Create user {0}...".format(args['name']))
        user.create()

    def modify(self, args, config, connection):
        user = User(args['name'], connection=connection)
        if not user.exists():
            print("Error: User does not exist: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            newuser = self._read(args['name'], args['json'])
            newuser.connection = user.connection
            user = newuser

        self.roles = []
        self._properties(user, args)
        if len(self.roles) > 0:
            user.set_role_names(self.roles)

        print("Modify user {0}...".format(args['name']))
        user.update(connection)

    def delete(self, args, config, connection):
        user = User.lookup(connection, args['name'])
        if user is None:
            return

        print("Delete user {0}...".format(args['name']))
        user.delete(connection)

    def get(self, args, config, connection):
        user = User(args['name'], connection=connection)
        if not user.exists():
            print("Error: User does not exist: {0}".format(args['name']))
            sys.exit(1)

        user.read()
        self.jprint(user)

    def _special_property(self, name, value):
        if name == 'role':
            self.roles.append(value)
        else:
            super()._special_property(name,value)

    def _read(self, name, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['user-name'] = name
        user = User.unmarshal(data)
        return user
