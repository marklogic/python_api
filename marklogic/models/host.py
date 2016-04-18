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
# Paul Hoehne       03/26/2015     Initial development
#

"""
Host related classes for manipulating MarkLogic hosts
"""

from __future__ import unicode_literals, print_function, absolute_import
import json
import logging
from marklogic.models.model import Model
from marklogic.connection import Connection
from marklogic.exceptions import UnexpectedManagementAPIResponse


class Host(Model):
    """
    The Host class encapsulates a MarkLogic host.
    """
    def __init__(self, name=None, connection=None, save_connection=True):
        """
        Create a host.
        """
        if name is None:
            self._config = {}
        else:
            self._config = {'host-name': name}

        self.name = name
        self.etag = None
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.host")
        self._just_initialized = False

    def host_name(self):
        """
        Returns the host name of the cluster member
        :return: The member host name
        """
        return self._get_config_property('host-name')

    def set_host_name(self, name):
        self._config['host-name'] = name

    def group_name(self):
        """
        The cluster member's group

        :return: Host's Group
        """
        return self._get_config_property('group')

    def set_group_name(self, name):
        self._config['group'] = name

    def bind_port(self):
        """
        The bind port of the cluster member

        :return: The host's bind port
        """
        return self._get_config_property('bind-port')

    def set_bind_port(self, port):
        self._config['bind-port'] = port

    def foreign_bind_port(self):
        """
        The foreign bind port.

        :return: The Host's foreign bind port
        """
        return self._get_config_property('foreign-bind-port')

    def set_foreign_bind_port(self, port):
        self._config['foreign-bind-port'] = port

    def zone(self):
        """
        The zone

        :return: The zone
        """
        return self._get_config_property('zone')

    def set_zone(self, zone):
        self._config['zone'] = zone

    def bootstrap_host(self):
        """
        Indicates if this is the bootstrap host

        :return:Bootstrap host indicator
        """
        return self._get_config_property('boostrap-host')

    def just_initialized(self):
        """
        Indicates if this host was just initialized. This method will
        only return True if the host was just initialized (i.e, returned
        by MarkLogic.instance_init()).

        :return:True or False
        """
        return self._just_initialized

    def _set_just_initialized(self):
        """
        Internal method used to specify that the host was just initialized.

        :return: The host object
        """
        self._just_initialized = True
        return self

    def read(self, connection=None):
        """
        Loads the host from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The host object
        """
        if connection is None:
            connection = self.connection
        host = Host.lookup(connection, self.name)
        if host is not None:
            self._config = host._config
            self.etag = host.etag

        return self

    def update(self, connection=None):
        """
        Save the configuration changes with the given connection.

        :param connection:The server connection

        :return: The host object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("hosts", self.name)
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)

        # In case we renamed it
        self.name = self._config['host-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def restart(self, connection=None):
        """
        Restart the host.

        :param connection:The server connection

        :return: The host object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("hosts", self.name, properties=None)
        struct = {'operation': 'restart'}
        response = connection.post(uri, payload=struct)
        return self

    def shutdown(self, connection=None):
        """
        Shutdown the host.

        :param connection:The server connection

        :return: None
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("hosts", self.name, properties=None)
        struct = {'operation': 'shutdown'}
        response = connection.post(uri, payload=struct)
        return None

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up an individual host within the cluster.

        :param name: The name of the host
        :param connection: A connection to a MarkLogic server
        :return: The host information
        """
        uri = connection.uri("hosts", name)
        response = connection.get(uri)
        if response.status_code == 200:
            result = Host.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    @classmethod
    def list(cls, connection):
        """
        Lists the names of hosts available on this cluster.

        :param connection: A connection to a MarkLogic server
        :return: A list of host names
        """

        uri = connection.uri("hosts")
        response = connection.get(uri)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            host_count = response_json['host-default-list']['list-items']['list-count']['value']

            result = []
            if host_count > 0:
                for item in response_json['host-default-list']['list-items']['list-item']:
                    result.append(item['nameref'])
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    @classmethod
    def unmarshal(cls, config):
        result = Host()
        result._config = config
        result.name = result._config['host-name']
        return result

    def marshal(self):
        struct = {}
        for key in self._config:
            struct[key] = self._config[key]
        return struct

    def join_cluster(self, cluster, cluster_connection=None):
        if cluster_connection is None:
            cluster_connection = cluster.connection

        xml = self._get_server_config()
        cfgzip = cluster._post_server_config(xml, cluster_connection)
        connection = Connection(self.host_name(), cluster_connection.auth)
        self._post_cluster_config(cfgzip, connection)

    def _get_server_config(self):
        """
        Obtain the server configuration. This is the data necessary for
        the first part of the handshake necessary to join a host to a
        cluster. The returned data is not intended for introspection.

        :return: The config. This is always XML.
        """
        connection = Connection(self.host_name(), None)
        uri = "http://{0}:8001/admin/v1/server-config".format(connection.host)
        response = connection.get(uri, accept="application/xml")
        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        return response.text  # this is always XML

    def _post_cluster_config(self, cfgzip, connection):
        """
        Send the cluster configuration to the the server that's joining
        the cluster. This is the second half of
        the handshake necessary to join a host to a cluster.

        :param connection: The connection credentials to use
        :param cfgzip: The ZIP payload from post_server_config()
        """
        uri = "{0}://{1}:8001/admin/v1/cluster-config" \
              .format(connection.protocol, connection.host)

        response = connection.post(uri, payload=cfgzip,
                                   content_type="application/zip")

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        data = json.loads(response.text)
