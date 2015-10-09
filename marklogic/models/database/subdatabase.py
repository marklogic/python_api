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
# Norman Walsh      08/18/2015     Initial development

"""
Classes for dealing with subdatabases
"""
from marklogic.models.model import Model

class Subdatabase:
    """
    A database subdatabase.
    """
    def __init__(self, database, cluster=None):
        """
        Create a subdatabase

        :param database: The name of the subdatabase.
        :param cluster: The name of the foreign cluster.
        """
        self._config = {
            'database-name': database
            }
        if cluster is not None:
            self._config['cluster-name'] = cluster

    def database(self):
        """
        The database.
        """
        return self._get_config_property('database-name')

    def set_database(self, database):
        """
        Set the database.
        """
        self._config['database-name'] = database
        return self

    def cluster(self):
        """
        The cluster name, or None.
        """
        return self._get_config_property('cluster-name')

    def set_database(self, cluster):
        """
        Set the cluster.
        """
        if cluster is None:
            if 'cluster-name' in self._config:
                del(self._config['cluster-name'])
        else:
            self._config['cluster-name'] = cluster
