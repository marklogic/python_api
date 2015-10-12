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
from requests.auth import HTTPDigestAuth
from marklogic.connection import Connection
from marklogic.cli.manager import Manager
from marklogic.models.cluster import LocalCluster
from marklogic.models.host import Host
from marklogic import MarkLogic

class ClusterManager(Manager):
    """
    The GroupManager performs operations on groups.
    """
    def __init__(self):
        self.logger = logging.getLogger("marklogic.cli")

    def modify(self, args, config, connection):
        cluster = LocalCluster(connection=connection)

        if args['json'] is not None:
            newclst = self._read(args['json'])
            newclst.connection = cluster.connection
            cluster = newclst

        self._properties(cluster, args)

        print("Modify cluster...")
        cluster.update(connection=connection)

    def get(self, args, config, connection):
        cluster = LocalCluster(connection=connection)
        cluster.read()
        self.jprint(cluster)

    def bootstrap_hosts(self, args, config, connection):
        cluster = LocalCluster(connection=connection)
        cluster.read()
        hosts = []
        for host in cluster.bootstrap_hosts():
            hosts.append(host.host_name())
        print(json.dumps(hosts, sort_keys=True, indent=2))

    def couple(self, args, config, connection):
        cluster = LocalCluster(connection=connection)
        cluster.read()

        try:
            username, password = re.split(":", args['couple_credentials'])
        except ValueError:
            print ("--couple-credentials value must be 'user:password':",
                   args['couple_credentials'])
            sys.exit(1)

        altconn = Connection(args['host'], HTTPDigestAuth(username, password))
        altcluster = LocalCluster(connection=altconn)

        cluster.couple(altcluster, connection=connection,
                       other_cluster_connection=altconn)

    def join(self, args, config, connection):
        cluster = LocalCluster(connection=connection)
        cluster.read()

        self.logger.info("Initializing {0}...".format(args['host']))
        MarkLogic.instance_init(args['host'])
        host = Host(args['host'])

        self.logger.info("Joining cluster...")
        cluster.add_host(host)

    def leave(self, args, config, connection):
        cluster = LocalCluster(connection=connection)
        cluster.read()

        self.logger.info("Removing {0} from cluster...".format(args['host']))
        cluster.remove_host(args['host'])

    def _read(self, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        cluster = LocalCluster.unmarshal(data)
        return cluster
