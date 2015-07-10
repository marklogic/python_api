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

import socket
import requests
import json
import logging
from .utilities.validators import validate_forest_availability
from .utilities.exceptions import UnexpectedManagementAPIResponse

"""
MarkLogic Forest support classes.
"""

class Forest:
    """
    Encapsulates a MarkLogic forest.  Can be added to a database configuration to create forests
    with specific options.  There are two types of attributes in Forest.  The properties can be
    changed after creation.  The config is the non-mutable state that is configured when the forest
    is created.
    """
    def __init__(self, name, host=None, data_directory=None, large_data_directory=None, fast_data_directory=None):
        self.properties = {
        }

        self.config = {
            'forest-name': name
        }

        if data_directory is not None:
            self.config['data-directory'] = data_directory

        if large_data_directory is not None:
            self.config['large-data-directory'] = large_data_directory

        if fast_data_directory is not None:
            self.config['fast-data-directory'] = fast_data_directory

        if host is not None:
            self.config['host'] = host
        else:
            self.config['host'] = socket.gethostname().lower()

        self.logger = logging.getLogger("marklogic")

    def host(self):
        """
        Return the hostname for this forest

        :return: The hostname
        """
        return self.config['host']

    def set_database(self, db='Documents'):
        """
        The database to which this forest belongs.

        :param db: A database name
        :return: The Forest object
        """
        self.config['database'] = db
        return self

    def database(self):
        """
        Return the database for the forest

        :return: The asociated database
        """
        if 'database' in self.config:
            return self.config['database']
        return None

    def data_directory(self):
        """
        Returns the data directory for the forest.

        :return: The data directory path
        """
        if 'data-directory' in self.config:
            return self.config['data-directory']
        return None

    def large_data_directory(self):
        """
        Return the large data directory for the forest

        :return:The large data directory path
        """
        if 'large-data-directory' in self.config:
            return self.config['large-data-directory']
        return None

    def fast_data_directory(self):
        """
        Return the fast data directory for the forest.

        :return:The fast data directory
        """
        if 'fast-data-directory' in self.config:
            return self.config['fast-data-directory']
        return None

    def set_availability(self, which='online'):
        """
        Indicate weather the forest is available.

        :param which: The availability of the forest
        :return: The Forest object
        """
        validate_forest_availability(which)
        self.properties['availability'] = which
        return self

    def availability(self):
        """
        Returns the availability status for the forest.

        :return: Availability status
        """
        if 'availability' in self.properties:
            return self.properties['availability']
        return None

    def forest_name(self):
        """
        Returns the name of the forest.

        :return: The forest name
        """
        return self.config['forest-name']

    def create(self, connection):
        """
        Creates the forest on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        uri = "http://{0}:{1}/manage/v2/forests".format(connection.host, connection.management_port)
        payload = {}
        payload.update(self.properties)
        payload.update(self.config)

        self.logger.debug("Creating forest: {0}".format(self.forest_name()))
        response = requests.post(uri, json=payload, auth=connection.auth)
        if response.status_code > 299:
            raise Exception(response.text)

        return Forest.lookup(connection, self.config['forest-name'])

    def save(self, connection):
        """
        Saves the updated forest configuration to the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        uri = "http://{0}:{1}/manage/v2/forests/{2}/properties".format(connection.host, connection.management_port,
                                                                       self.config['forest-name'])
        response = requests.put(uri, json=self.config, auth=connection.auth)

        if response.status_code > 299:
            raise Exception(response.text)

        return self

    def remove(self, connection):
        """
        Delete a forest from the MarkLogic server.

        :param connection: The connection to a MerkLogic server
        :return: The Forest object
        """
        uri = "http://{0}:{1}/manage/v2/forests/{2}?level=full".format(connection.host, connection.management_port,
                                                                       self.config[u'forest-name'])
        response = requests.delete(uri, auth=connection.auth)

        if response.status_code > 299 and not response.status_code == 404:
            raise Exception(response.text)

        return self

    @classmethod
    def lookup(cls, conn, name):
        """
        Look up a forest's configuration from the MarkLogic server.

        :param name: The name of the forest
        :param connection: The connection to a MarkLogic server
        :return: The Forest object
        """
        result = Forest('temp')

        uri = "http://{0}:{1}/manage/v2/forests/{2}/properties".format(conn.host, conn.management_port, name)
        response = requests.get(uri, auth=conn.auth, headers={'accept': 'application/json'})
        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        result.properties = json.loads(response.text)

        uri='http://{0}:{1}/manage/v2/forests/{2}?view=config'.format(conn.host, conn.management_port, name)
        response = requests.get(uri, auth=conn.auth, headers={'accept': 'application/json'})
        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        response_json = json.loads(response.text)
        result.config = response_json['forest-config']['config-properties']
        result.config['forest-name'] = response_json['forest-config']['name']

        for relation_group in response_json['forest-config']['relations']['relation-group']:
            if relation_group['typeref'] == 'hosts':
                result.config['host'] = relation_group['relation'][0]['nameref']

        return result
