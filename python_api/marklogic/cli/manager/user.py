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

    def create(self, args, config, connection):
        user = User(args['name'], args['password'], connection=connection)
        if user.exists():
            print("Error: User already exists: {0}".format(args['name']))
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

                if name == "description":
                    user.set_description(value)
                elif name == "external-name":
                    user.add_external_name(value)
                elif name == "role":
                    user.add_role_name(value)
                elif name == "permission":
                    print ("Permissions aren't supported yet!")
                elif name == "collection":
                    user.add_collection(value)
                else:
                    print ("User create does not support property: {0}"
                           .format(name))
                    sys.exit(1)

        print("Create user {0}...".format(args['name']))
        user.create()

    def modify(self, args, config, connection):
        user = User(args['name'], connection=connection)
        if not user.exists():
            print("Error: User does not exist: {0}".format(args['name']))
            sys.exit(1)

        methods = inspect.getmembers(user, predicate=inspect.ismethod)
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

        print("Modify user {0}...".format(args['name']))
        user.update(connection)

    def delete(self, args, config, connection):
        user = User.lookup(connection, args['name'])
        if user is None:
            return

        print("Delete user {0}...".format(args['name']))
        user.delete(connection)

