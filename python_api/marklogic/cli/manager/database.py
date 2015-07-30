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

import json
import logging
import re
import sys
from marklogic.models.database import Database

class DatabaseManager:
    """
    The DatabaseManager performs operations on databases.
    """
    def __init__(self):
        pass

    def create(self, args, connection):
        database = Database(args['name'], args['forest_host'],
                            connection=connection)
        if database.exists():
            print("Error: Database already exists: {0}".format(args['name']))
            sys.exit(1)

        forests = []

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

                if name == 'forest':
                    forests.append(value)
                else:
                    print("Unsupported property: {0}".format(prop))
                    sys.exit(1)

        if len(forests) > 0:
            database.set_forest_names(forests)

        database.create()

    def delete(self, args, connection):
        database = Database(args['name'], connection=connection)
        if not database.exists():
            return

        forest_delete = args['forest_delete']
        database.delete(forest_delete,connection)


