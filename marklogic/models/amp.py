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
# Norman Walsh      24 Mar 2016    Initial development
#

"""
Amp related classes for manipulating MarkLogic amps
"""

# FIXME: add docstrings
# FIXME: check types of arguments

import json
import logging
from marklogic.utilities import PropertyLists
from marklogic.models.model import Model
from marklogic.exceptions import UnexpectedManagementAPIResponse


class Amp(Model, PropertyLists):
    """
    The Amp class encapsulates a MarkLogic amp.
    """

    def __init__(self, local_name=None, namespace=None, document_uri=None,
                 modules_database=None, role=None,
                 connection=None, save_connection=True):
        """
        Create an amp
        """
        self._config = {}
        if local_name is not None:
            self._config['local-name'] = local_name
        if namespace is not None:
            self._config['namespace'] = namespace
        if document_uri is not None:
            self._config['document-uri'] = document_uri
        if modules_database is not None:
            self._config['modules-database'] = modules_database
        if role is not None:
            if isinstance(role, list):
                self._config['role'] = role
            else:
                self._config['role'] = [role]

        self.etag = None
        if save_connection:
            self.connection = connection
        else:
            self.connection = None

        self.logger = logging.getLogger("marklogic.amp")

    def set_connection(self, connection, save_connection):
        if save_connection:
            self.connection = connection
        return self

    def local_name(self):
        return self._get_config_property('local-name')

    def set_local_name(self, value):
        self._config['local-name'] = value
        return self

    def namespace(self):
        return self._get_config_property('namespace')

    def set_namespace(self, value):
        self._config['namespace'] = value
        return self

    def document_uri(self):
        return self._get_config_property('document-uri')

    def set_document_uri(self, value):
        self._config['document-uri'] = value
        return self

    def modules_database(self):
        return self._get_config_property('modules-database')

    def set_modules_database(self, value):
        self._config['modules-database'] = value
        return self

    def role_names(self):
        """
        Returns the roles for this user

        :return: The list of roles
        """
        return self.get_property_list('role')

    def set_role_names(self, roles):
        """
        Sets the roles for this user

        :return: The user object
        """
        return self.set_property_list('role', roles)

    def add_role_name(self, add_role):
        """
        Adds the specified role to roles for this user

        :return: The user object
        """
        return self.add_to_property_list('role', add_role)

    def remove_role_name(self, remove_role):
        """
        Removes the specified role to roles for this user

        :return: The user object
        """
        return self.remove_from_property_list('role', remove_role)

    def create(self, connection=None):
        """
        Create a new amp.

        :param connection: The server connection

        :return: The amp object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("amps")

        struct = self.marshal()

        self.logger.debug("Creating {0} amp".format(self.local_name()))

        response = connection.post(uri, payload=struct)

        if response.status_code != 201:
            raise UnexpectedManagementAPIResponse(response.text)

        if 'etag' in response.headers:
            self.etag = response.headers['etag']

        return self

    def read(self, connection=None):
        """
        Loads the amp from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The amp object
        """
        if connection is None:
            connection = self.connection

        amp = Amp.lookup(connection, self.local_name(), self.namespace(),
                         self.document_uri(), self.modules_database())

        if amp is not None:
            self._config = amp._config
            self.etag = amp.etag

        return self

    def update(self, connection=None):
        """
        Save the configuration changes with the given connection.

        :param connection:The server connection

        :return: The amp object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("amps", self.local_name(),
                             parameters=self._params())

        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)
        if response.status_code != 204:
            raise UnexpectedManagementAPIResponse(response.text)

        if 'etag' in response.headers:
            self.etag = response.headers['etag']

        return self

    def delete(self, connection=None):
        """
        Remove the given amp.

        :param connection: The server connection

        :return: The amp object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("amps", self.local_name(), properties=None,
                             parameters=self._params())

        response = connection.delete(uri)
        if response.status_code != 204:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def exists(self, connection=None):
        """
        Returns true if (and only if) the amp exits.

        :param connection: The connection to the MarkLogic database
        :return: True if the amp exists
        """
        if connection is None:
            connection = self.connection

        amp = Amp.lookup(connection, self.local_name(), self.namespace(),
                         self.document_uri(), self.modules_database())

        return amp is not None

    @classmethod
    def lookup(cls, connection, local_name, namespace, document_uri,
               modules_database=None):
        """Look up an individual amp.

        :param connection: A connection to a MarkLogic server
        :param local_name: The name of the amped function
        :param namespace: The namespace URI of the amped function
        :param document_uri: The URI of the document that contains the
        amped function
        :return: The amp.
        """
        params = ["namespace="+namespace,
                  "document-uri="+document_uri]
        if modules_database is not None:
            params.append("modules-database="+modules_database)

        uri = connection.uri("amps", local_name, parameters=params)
        response = connection.get(uri)
        if response.status_code == 200:
            result = Amp.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    @classmethod
    def list(cls, connection):
        """
        Lists the amps on this cluster.

        :param connection: A connection to a MarkLogic server
        :return: A list of amps.
        """

        uri = connection.uri("amps")
        response = connection.get(uri)

        # This one isn't like all the others because they're compound
        # Should return the IDs but the Management API doesn't (yet) allow
        # access by only the ID.
        if response.status_code == 200:
            response_json = json.loads(response.text)
            amp_count = response_json['amp-default-list']['list-items']['list-count']['value']

            result = []
            if amp_count > 0:
                for item in response_json['amp-default-list']['list-items']['list-item']:
                    result.append({"local-name": item['nameref'],
                                   "namespace": item['namespace'],
                                   "document-uri": item['document-uri']})
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    @classmethod
    def unmarshal(cls, config):
        result = Amp()

        result._config = config
        return result

    def marshal(self):
        struct = {}
        for key in self._config:
            struct[key] = self._config[key]
        return struct

    def _params(self):
        parameters = []
        for key in ["namespace", "document-uri", "modules-database"]:
            if key in self._config:
                parameters.append(key + "=" + self._config[key])
        return parameters
