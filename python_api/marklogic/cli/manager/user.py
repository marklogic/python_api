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

import json
import logging
import re
import sys
from marklogic.models.user import User

class UserManager:
    """
    The UserManager performs operations on users.
    """
    def __init__(self):
        pass

    def create(self, args, connection):
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

        user.create()

    def delete(self, args, connection):
        user = User.lookup(connection, args['name'])
        if user is None:
            return

        user.delete(connection)

