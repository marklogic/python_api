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

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.forest import Forest
from marklogic.models.database import Database
from marklogic.models.cluster import LocalCluster

class ForestManager(Manager):
    """
    The ForestManager performs operations on forests.
    """
    def __init__(self):
        self.logger = logging.getLogger("marklogic.cli")
        pass

    def list(self, args, config, connection):
        forests = Forest.list(connection)
        print(json.dumps(forests, sort_keys=True, indent=2))

    def create(self, args, config, connection):
        name = args['name']
        host = args['forest_host']

        if args['json'] is not None:
            forest = self._read(name, args['json'], connection=connection)
            name = forest.forest_name()
            host = forest.host()
        else:
            forest = Forest(name, host, connection=connection)

        if forest.exists():
            self.logger.error("Forest already exists: {0}".format(name))
            sys.exit(1)

        self._properties(forest, args)
        dbname = forest.database()

        # Strip out properties that we know the server will reject
        cluster = LocalCluster(connection)
        cluster.read()
        if cluster.security_version() is None:
            for key in ['database-replication', 'failover-enable']:
                if key in forest._config:
                    del(forest._config[key])
                    self.logger.debug("Ignoring {0}, not supported by server"
                                      .format(key))

        if dbname is not None:
            database = Database(dbname)
            database.read(connection)
        else:
            database = None

        self.logger.info("Create forest {0}...".format(name))
        forest.create(connection=connection)

        if database is not None:
            database.add_forest_name(forest.forest_name())
            database.update(connection)

    def modify(self, args, config, connection):
        name = args['name']
        forest = Forest(name, connection=connection)
        if not forest.exists():
            print("Error: Forest does not exist: {0}".format(name))
            sys.exit(1)

        if args['json'] is not None:
            forest = self._read(None, args['json'], connection=connection)
            if forest.host() is None and 'forest_host' in args:
                forest.set_host(args['forest_host'])
            forest.name = name

        self._properties(forest, args)
        print("Modify forest {0}...".format(name))
        forest.update(connection=connection)

    def delete(self, args, config, connection):
        forest = Forest(args['name'], args['forest_host'], connection=connection)
        if not forest.exists():
            return

        level = args['level']
        replicas = args['replicas']

        print("Delete forest {0}...".format(args['name']))
        forest.delete(level,replicas,connection)

    def get(self, args, config, connection):
        forest = Forest(args['name'], connection=connection)
        if not forest.exists():
            print("Error: Forest does not exist: {0}".format(args['name']))
            sys.exit(1)

        forest.read()
        self.jprint(forest)

    def _read(self, name, jsonfile,
              connection=None, save_connection=True):
        jf = open(jsonfile).read()
        data = json.loads(jf)

        if name is not None:
            data['forest-name'] = name

        if 'database' in data:
            del(data['database'])

        forest = Forest.unmarshal(data,
                                  connection=connection,
                                  save_connection=save_connection)

        return forest
