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
A class to manage clusters.
"""

import inspect, json, logging, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.cluster import ForeignCluster

class ForeignClusterManager(Manager):
    """
    The ForiengClusterManager performs operations on foreign clusters.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        print(ForeignCluster.list(connection))

    def modify(self, args, config, connection):
        cluster = ForeignCluster(args['name'],connection=connection)

        if args['json'] is not None:
            newclst = self._read()
            newclst.connection = cluster.connection
            cluster = newclst

        self._properties(cluster, args)

        print("Modify cluster...")
        cluster.update(connection=connection)

    def get(self, args, config, connection):
        cluster = ForeignCluster(args['name'], connection=connection)
        cluster.read()
        self.jprint(cluster)

    def bootstrap_hosts(self,args, config, connection):
        cluster = ForeignCluster(connection=connection)
        cluster.read()
        hosts = []
        for host in cluster.bootstrap_hosts():
            hosts.append(host.host_name())
        print(json.dumps(hosts, sort_keys=True, indent=2))

    def _read(self):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        cluster = ForeignCluster.unmarshal(data)
        return cluster
