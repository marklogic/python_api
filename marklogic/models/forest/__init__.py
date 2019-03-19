# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

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
# Paul Hoehne       03/01/2015     Initial development
#

import json
import logging
from marklogic.exceptions import UnexpectedManagementAPIResponse, UnsupportedOperation
from marklogic.utilities.validators import validate_forest_availability, validate_boolean
from marklogic.models.model import Model
from marklogic.models.forest.scheduledbackup import ScheduledForestBackup
from marklogic.models.forest.replica import ForestReplica
from marklogic.utilities import PropertyLists

"""
MarkLogic Forest support classes.
"""

class Forest(Model,PropertyLists):
    """
    Encapsulates a MarkLogic forest. Can be added to a database
    configuration to create forests with specific options.
    """

    def __init__(self, name, host=None, connection=None, save_connection=True):
        self._config = {'forest-name': name}
        if host is not None:
            self._config['host'] = host
        else:
            self._config['host'] = '$ML-LOCALHOST'

        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None

        self.name = name
        self.host_name = host
        self.created = False
        self.etag = None
        self.logger = logging.getLogger("marklogic")

    def availability(self):
        """
        Returns the availability status for the forest.

        :return: Availability status
        """
        return self._get_config_property('availability')

    def set_availability(self, which='online'):
        """
        Indicate weather the forest is available.

        :param which: The availability of the forest
        :return: The Forest object
        """
        validate_forest_availability(which)
        return self._set_config_property('availability', which)

    def data_directory(self):
        """
        Returns the data directory for the forest.

        :return: The data directory path
        """
        return self._get_config_property('data-directory')

    def set_data_directory(self, path):
        return self._set_config_property('data-directory', path)

    def large_data_directory(self):
        """
        Return the large data directory for the forest

        :return:The large data directory path
        """
        return self._get_config_property('large-data-directory')

    def set_large_data_directory(self, path):
        return self._set_config_property('large-data-directory', path)

    def fast_data_directory(self):
        """
        Return the fast data directory for the forest.

        :return:The fast data directory
        """
        return self._get_config_property('fast-data-directory')

    def set_fast_data_directory(self, path):
        return self._set_config_property('fast-data-directory', path)

    def fast_data_max_size(self):
        """
        Return the fast data max size for the forest.

        :return:The fast data maxs ize
        """
        return self._get_config_property('fast-data-max-size')

    def set_fast_data_max_size(self, size):
        return self._set_config_property('fast-data-max-size', size)

    def database(self):
        return self._get_config_property('database')

    def set_database(self,name):
        if name is None:
            del self._config['database']
            return self
        else:
            return self._set_config_property('database', name)

    def database_replication(self):
        raise UnsupportedOperation("Not implemented yet")

    def set_database_replication(self,value):
        raise UnsupportedOperation("Not implemented yet")

    def enabled(self):
        return self._get_config_property('enabled')

    def set_enabled(self, enabled):
        validate_boolean(enabled)
        return self._set_config_property('enabled', enabled)

    def failover_enable(self):
        return self._get_config_property('failover-enable')

    def set_failover_enable(self, enable):
        validate_boolean(enable)
        return self._set_config_property('failover-enable', enable)

    def failover_host_names(self):
        # FIXME:
        return self._get_config_property('failover-host')

    def set_failover_host_names(self, hosts):
        # FIXME:
        return self._set_config_property('failover-host', hosts)

    def scheduled_backups(self):
        """
        The scheduled backups.
        """
        return self._get_config_property('forest-backup')

    def set_scheduled_backups(self, backups):
        """
        Set the scheduled backups.
        """
        return self.set_property_list('forest-backup',
                                      backups, ScheduledForestBackup)

    def add_scheduled_backup(self, backup):
        """
        Add a scheduled backup.
        """
        return self.add_to_property_list('forest-backup',
                                         backup, ScheduledForestBackup)

    def remove_scheduled_backup(self, backup):
        """
        Remove a scheduled backup.
        """
        return self.remove_from_property_list('forest-backup',
                                              backup, ScheduledForestBackup)

    def forest_name(self):
        name = self._get_config_property('forest-name')
        if name is None:
            return self.name
        else:
            return name

    def set_forest_name(self,name):
        return self._set_config_property('forest-name', name)

    def forest_replicas(self):
        """
        Forest replicas.
        """
        return self._get_config_property('forest-replica')

    def set_forest_replicas(self, replicas):
        return self.set_property_list('forest-replica', replicas, ForestReplica)

    def add_forest_replica(self, replica):
        return self.add_to_property_list('forest-replica', replica, ForestReplica)

    def remove_forest_replicas(self, replica):
        return self.remove_from_property_list('forest-replica',
                                              replica, ForestReplica)

    def host(self):
        """
        Return the hostname for this forest

        :return: The hostname
        """
        name = self._get_config_property('host')
        if name is None:
            return self.host_name
        else:
            return name

    def set_host(self, name):
        """
        Set the hostname for this forest

        :return: the Forest
        """
        return self._set_config_property('host',name)

    def range(self):
        return self._get_config_property('range')

    def set_range(self, therange):
        return self._set_config_property('range', therange)

    def rebalancer_enable(self):
        return self._get_config_property('rebalancer-enable')

    def set_rebalancer_enable(self, enable):
        validate_boolean(enable)
        return self._set_config_property('rebalancer-enable', enable)

    def updates_allowed(self):
        return self._get_config_property('updates-allowed')

    def set_updates_allowed(self, allowed):
        return self._set_config_property('updates-allowed', allowed)

    def exists(self, connection=None):
        """
        Checks to see if the forest exists on the server.

        :param connection: The connection to a MarkLogic server
        :return: True if the forest exists
        """
        if connection is None:
            connection = self.connection

        forest = Forest.lookup(connection, self.forest_name())
        return forest is not None

    def create(self, connection=None):
        """
        Creates the forest on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("forests")
        struct = self.marshal()
        response = connection.post(uri, payload=struct)
        return self

    def read(self, connection=None):
        """
        Loads the forest from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The server object
        """
        if connection is None:
            connection = self.connection

        forest = Forest.lookup(connection, self.forest_name())
        if forest is not None:
            self._config = forest._config
            self.etag = forest.etag

        return self

    def update(self, connection=None):
        """
        Saves the updated forest _configuration to the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("forests", self.name)
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)

        # In case we renamed it
        self.name = self._config['forest-name']
        return self

    def delete(self, level="full", replicas="delete", connection=None):
        """
        Delete a forest from the MarkLogic server.

        :param connection: The connection to a MerkLogic server
        :return: The Forest object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("forests", self.name, properties=None,
                             parameters=["level="+level,
                                         "replicas="+replicas])

        response = connection.delete(uri)
        return self

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up a forest's properties from the MarkLogic server.

        :param name: The name of the forest
        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        uri = connection.uri("forests", name)
        response = connection.get(uri)

        result = None
        if response.status_code == 200:
            result = Forest.unmarshal(json.loads(response.text))
            result.name = name
            if 'etag' in response.headers:
                result.etag = response.headers['etag']

        return result

    @classmethod
    def list(cls, connection):
        uri = connection.uri("forests")
        response = connection.get(uri)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            list_items = response_json['forest-default-list']['list-items']
            db_count = list_items['list-count']['value']

            result = []
            if db_count > 0:
                for item in list_items['list-item']:
                    result.append(item['nameref'])
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    @classmethod
    def unmarshal(cls, config, connection=None, save_connection=True):
        result = Forest("temp",
                        connection=connection, save_connection=save_connection)
        result._config = config
        result.name = result._config['forest-name']

        logger = logging.getLogger("marklogic.forest")

        atomic = {'availability', 'data-directory',
                  'database-replication', 'enabled',
                  'failover-enable', 'fast-data-directory', 'fast-data-max-size',
                  'forest-name', 'host', 'large-data-directory',
                  'range', 'rebalancer-enable', 'updates-allowed',
                  'database'
                 }

        for key in result._config:
            olist = []

            if key in atomic:
                pass
            elif key == 'forest-backup':
                for backup in result._config['forest-backup']:
                    #logger.debug(backup)
                    temp = None
                    if backup['backup-type'] == 'minutely':
                        temp = ScheduledForestBackup.minutely(
                            backup['backup-directory'],
                            backup['backup-period'])
                    elif backup['backup-type'] == 'hourly':
                        minute = int(backup['backup-start-time'].split(':')[1])
                        temp = ScheduledForestBackup.hourly(
                            backup['backup-directory'],
                            backup['backup-period'],
                            minute)
                    elif backup['backup-type'] == 'daily':
                        temp = ScheduledForestBackup.daily(
                            backup['backup-directory'],
                            backup['backup-period'],
                            backup['backup-start-time'])
                    elif backup['backup-type'] == 'weekly':
                        temp = ScheduledForestBackup.weekly(
                            backup['backup-directory'],
                            backup['backup-period'],
                            backup['backup-day'],
                            backup['backup-start-time'])
                    elif backup['backup-type'] == 'monthly':
                        temp = ScheduledForestBackup.monthly(
                            backup['backup-directory'],
                            backup['backup-period'],
                            backup['backup-month-day'],
                            backup['backup-start-time'])
                    elif backup['backup-type'] == 'once':
                        temp = ScheduledForestBackup.once(
                            backup['backup-directory'],
                            backup['backup-start-date'],
                            backup['backup-start-time'])
                    else:
                        raise UnexpectedManagementAPIResponse("Unparseable backup")
                    temp._config['backup-id'] = backup['backup-id']
                    olist.append(temp)
                result._config['forest-backup'] = olist
            elif key == 'forest-replica':
                for rep in result._config['forest-replica']:
                    temp = ForestReplica(rep['replica-name'], rep['host'],
                                         rep['data-directory'],
                                         rep['large-data-directory'],
                                         rep['fast-data-directory'])
                    olist.append(temp)
                result._config['forest-replica'] = olist
            else:
                logger.warning("Unexpected forest property: " + key)

        return result

    def marshal(self):
        struct = { }
        for key in self._config:
            if (key == 'forest-backup'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            elif (key == 'forest-replica'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            else:
                struct[key] = self._config[key];
        return struct
