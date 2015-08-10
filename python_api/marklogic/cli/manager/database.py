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
A class to manage databases.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.database import Database

class DatabaseManager(Manager):
    """
    The DatabaseManager performs operations on databases.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        print(Database.list(connection))

    def create(self, args, config, connection):
        database = Database(args['name'], args['forest_host'],
                            connection=connection)
        if database.exists():
            print("Error: Database already exists: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            database = self._read(args['name'], args['json'])

        self.forests = []
        self._properties(database, args)
        if len(self.forests) > 0:
            database.set_forest_names(self.forests)

        print("Create database {0}...".format(args['name']))
        database.create()

    def modify(self, args, config, connection):
        database = Database(args['name'], connection=connection)
        if not database.exists():
            print("Error: Database does not exist: {0}".format(args['name']))
            sys.exit(1)

        if args['json'] is not None:
            database = self._read(args['name'], args['json'])

        self.forests = []
        self._properties(database, args)
        if len(self.forests) > 0:
            database.set_forest_names(self.forests)

        print("Modify database {0}...".format(args['name']))
        database.update(connection=connection)

    def delete(self, args, config, connection):
        database = Database(args['name'], connection=connection)
        if not database.exists():
            return

        print("Delete database {0}...".format(args['name']))
        forest_delete = args['forest_delete']
        database.delete(forest_delete,connection)

    def get(self, args, config, connection):
        database = Database(args['name'], connection=connection)
        if not database.exists():
            print("Error: Database does not exist: {0}".format(args['name']))
            sys.exit(1)

        database.read()
        self.jprint(database)

    def _special_property(self, name, value):
        if name == 'forest':
            self.forests.append(value)
        else:
            super()._special_property(name,value)

    def _read(self, name, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        data['database-name'] = name
        database = Database.unmarshal(data)
        return database
