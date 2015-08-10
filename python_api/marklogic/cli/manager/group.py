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
# Norman Walsh      9 August 2015  Initial development
#

"""
A class to manage groups.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.group import Group

class GroupManager(Manager):
    """
    The GroupManager performs operations on groups.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        print(Group.list(connection))

    def create(self, args, config, connection):
        group = Group(args['name'], connection=connection)
        if group.exists():
            print("Error: Database already exists: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            group = self._read(args['name'], args['json'])

        self._properties(group, args)

        print("Create group {0}...".format(args['name']))
        group.create()

    def modify(self, args, config, connection):
        group = Group(args['name'], connection=connection)
        if not group.exists():
            print("Error: Group does not exist: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            group = self._read(args['name'], args['json'])

        self._properties(group, args)

        print("Modify group {0}...".format(args['name']))
        group.update(connection=connection)

    def delete(self, args, config, connection):
        group = Group(args['name'], connection=connection)
        if not group.exists():
            return

        print("Delete group {0}...".format(args['name']))
        group.delete(connection)

    def get(self, args, config, connection):
        group = Group(args['name'], connection=connection)
        if not group.exists():
            print("Error: Group does not exist: {0}".format(args['name']))
            sys.exit(1)

        group.read()
        self.jprint(group)

    def _read(self, name, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['group-name'] = name
        group = Group.unmarshal(data)
        return group
