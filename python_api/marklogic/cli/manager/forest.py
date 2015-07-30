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

"""
A class to create forests
"""

import json
import logging
import re
import sys
from marklogic.models.forest import Forest
from marklogic.models.database import Database

class ForestManager:
    """
    The ForestManager performs operations on forests.
    """
    def __init__(self):
        pass

    def create(self, args, connection):
        forest = Forest(args['name'], args['forest_host'], connection=connection)
        if forest.exists():
            print("Error: Forest already exists: {0}".format(args['name']))
            sys.exit(1)

        dbname = None

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

                if name == 'database':
                  dbname = value
                elif name == 'data-directory':
                  forest.set_data_directory(value)
                elif name == 'large-data-directory':
                  forest.set_large_data_directory(value)
                elif name == 'fast-data-directory':
                  forest.set_fast_data_directory(value)
                elif name == 'availability':
                  forest.set_availability(value)
                elif name == 'rebalancer-enable':
                  forest.set_rebalancer_enable(value)
                else:
                  print ("Forest create does not support property: {0}"
                         .format(name))
                  sys.exit(1)

        if dbname is not None:
            database = Database(dbname)
            database.read(connection)
        else:
            database = None

        forest.create()

        if database is not None:
            database.add_forest_name(forest.forest_name())
            database.update(connection)

    def delete(self, args, connection):
        forest = Forest(args['name'], args['forest_host'], connection=connection)
        if not forest.exists():
            return

        level = args['level']
        replicas = args['replicas']

        forest.delete(level,replicas,connection)


