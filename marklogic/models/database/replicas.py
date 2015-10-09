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
# Norman Walsh      08/07/2015     Initial development

from marklogic.models.model import Model

"""
Classes for dealing with replicas.
"""

class ForeignReplica(Model):
    """
    A database foreign replica.
    """
    def __init__(self, cluster_name, database_name, connect_by_name,
                       lag_limit, enabled=True, queue_size=10):
        """
        Create a foreign replica.

        :param cluster_name: The name of the foreign cluster
        :param database_name: The name of the foreign database
        :param connect_by_name: Connect forests by name?
        :param lag_limt: The lag limit
        :param enabled: Enable replication?
        :param queue_size: Size of queue
        """
        self._config = {
            'foreign-cluster-name': cluster_name,
            'foreign-database-name': database_name,
            'connect-forests-by-name': connect_by_name,
            'lag-limit': lag_limit,
            'replication-enabled': enabled,
            'queue-size': queue_size
            }

    def foreign_cluster_name(self):
        self._get_config_property('foreign-cluster-name')

    def set_foreign_cluster_name(self, value):
        self._set_config_property('foreign-cluster-name', value)

    def foreign_database_name(self):
        self._get_config_property('foreign-database-name')

    def set_foreign_database_name(self, value):
        self._set_config_property('foreign-database-name', value)

    def connect_forests_by_name(self):
        self._get_config_property('connect-forests-by-name')

    def set_connect_forests_by_name(self, value):
        self._set_config_property('connect-forests-by-name', value)

    def lag_limit(self):
        self._get_config_property('lag-limit')

    def set_lag_limit(self, value):
        self._set_config_property('lag-limit', value)

    def replication_enabled(self):
        self._get_config_property('replication-enabled')

    def set_replication_enabled(self, value):
        self._set_config_property('replication-enabled', value)

    def queue_size(self):
        self._get_config_property('queue-size')

    def set_queue_size(self, value):
        self._set_config_property('queue-size', value)

class ForeignMaster(Model):
    """
    A database foreign master.
    """
    def __init__(self, cluster_name, database_name, connect_by_name):
        """
        Create a foreign master.

        :param cluster_name: The name of the foreign cluster
        :param database_name: The name of the foreign database
        :param connect_by_name: Connect forests by name?
        """
        self._config = {
            'foreign-cluster-name': cluster_name,
            'foreign-database-name': database_name,
            'connect-forests-by-name': connect_by_name
            }

    def foreign_cluster_name(self):
        self._get_config_property('foreign-cluster-name')

    def set_foreign_cluster_name(self, value):
        self._set_config_property('foreign-cluster-name', value)

    def foreign_database_name(self):
        self._get_config_property('foreign-database-name')

    def set_foreign_database_name(self, value):
        self._set_config_property('foreign-database-name', value)

    def connect_forests_by_name(self):
        self._get_config_property('connect-forests-by-name')

    def set_connect_forests_by_name(self, value):
        self._set_config_property('connect-forests-by-name', value)
