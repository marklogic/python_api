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
# Norman Walsh      17 July 2015   Initial development
#

"""
Cluster class for manipulating MarkLogic clusters
"""

from __future__ import unicode_literals, print_function, absolute_import
import requests
import json
import time
import logging
from http.client import BadStatusLine
from marklogic.models.connection import Connection
from requests.packages.urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError
from marklogic.models.utilities.exceptions import *
from marklogic.models.host import Host

class Cluster:
    """
    The Cluster class encapsulates a MarkLogic host.
    """
    def __init__(self,connection=None,save_connection=True):
        """
        Create a cluster.
        """
        self._config = {}
        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic")

    def cluster_id(self):
        return self._config['cluster-id']

    def cluster_name(self):
        return self._config['cluster-name']

    def set_cluster_name(self, name):
        self._config['cluster-name'] = name

    def bootstrap_hosts(self):
        return self._config['bootstrap-host']

    def read(self, connection=None):
        if connection is None:
            connection = self.connection

        cluster = Cluster.lookup(connection)

        if cluster is not None:
            self._config = cluster._config
            self.etag = cluster.etag
            self.name = cluster._config['cluster-name']

        return self

    def update(self, connection=None):
        if connection is None:
            connection = self.connection
        uri = "http://{0}:{1}/manage/v2/properties".format(
            connection.host, connection.management_port)

        headers = {'accept': 'application/json'}
        if self.etag is not None:
            headers['if-match'] = self.etag

        struct = self.marshal()
        response = requests.put(uri, json=struct, auth=connection.auth,
                                headers=headers)

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        if response.status_code == 202:
            data = json.loads(response.text)
            Host.wait_for_restart(connection,
                                  data["restart"]["last-startup"][0]["value"])

        # In case we renamed it
        self.name = self._config['cluster-name']

        return self

    @classmethod
    def lookup(cls, connection):
        uri = "http://{0}:{1}/manage/v2/properties".format(
            connection.host, connection.management_port)

        result = None
        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})
        if response.status_code == 200:
            result = Cluster.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
        elif response.status_code != 404:
            raise UnexpectedManagementAPIResponse(response.text)
        return result

    @classmethod
    def unmarshal(cls, config):
        result = Cluster()
        result._config = config
        result.name = result._config['cluster-name']

        olist = []
        if 'bootstrap-host' in result._config:
            for index in result._config['bootstrap-host']:
                temp = BootstrapHost(index['bootstrap-host-id'],
                                     index['bootstrap-host-name'],
                                     index['bootstrap-connect-port'])
                olist.append(temp)
        result._config['bootstrap-host'] = olist

        return result

    def marshal(self):
        struct = { }
        for key in self._config:
            if (key == 'bootstrap-host'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            else:
                struct[key] = self._config[key];
        return struct

    def add_host(self, host, connection=None):
        if connection is None:
            connection = self.connection

        xml = host._get_server_config()
        cfgzip = self._post_server_config(xml,connection)

        host_connection = Connection(host.host_name(), connection.auth)
        host._post_cluster_config(cfgzip,host_connection)

    def couple(self, other_cluster, connection=None, other_cluster_connection=None):
        if connection is None:
            connection = self.connection
        if other_cluster_connection is None:
            other_cluster_connection = other_cluster.connection

        self.read(connection)
        other_cluster.read(other_cluster_connection)

        uri = "http://{0}:{1}/manage/v2/clusters".format(
            connection.host, connection.management_port)

        headers = {'accept': 'application/json'}

        struct = other_cluster.marshal()
        response = requests.post(uri, json=struct, auth=connection.auth,
                                 headers=headers)

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        if response.status_code == 202:
            data = json.loads(response.text)
            Host.wait_for_restart(connection,
                                  data["restart"]["last-startup"][0]["value"])

        uri = "http://{0}:{1}/manage/v2/clusters".format(
            other_cluster_connection.host, other_cluster_connection.management_port)

        struct = self.marshal()
        response = requests.post(uri, json=struct, auth=connection.auth,
                                 headers=headers)

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        if response.status_code == 202:
            data = json.loads(response.text)
            Host.wait_for_restart(connection,
                                  data["restart"]["last-startup"][0]["value"])

    def _post_server_config(self,xml,connection):
        """
        Send the server configuration to the a bootstrap host on the
        cluster to which you wish to couple. This is the first half of
        the handshake necessary to join a host to a cluster. The results
        are not intended for introspection.

        :param connection: The connection credentials to use
        :param xml: The XML payload from get_server_config()
        :return: The cluster configuration as a ZIP file.
        """
        uri = "http://{0}:8001/admin/v1/cluster-config".format(connection.host)

        payload = { 'group': 'Default',
                    'server-config': xml }

        self.logger.debug("Posting server configuration to {0}"
                          .format(connection.host))
        response = requests.post(uri, data=payload, auth=connection.auth,
                                 headers={'content-type': 'application/x-www-form-urlencoded',
                                          'accept': 'application/json'})

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        return response.content

class BootstrapHost:
    """
    The BootstrapHost class encapsulates a MarkLogic cluster bootstrap host.
    """
    def __init__(self,host_id,host_name,connect_port):
        self._config = {'bootstrap-host-id': host_id,
                        'bootstrap-host-name': host_name,
                        'bootstrap-connect-port': connect_port}
        self.etag = None
        self.logger = logging.getLogger("marklogic")

    def host_id(self):
        return self._config['bootstrap-host-id']

    def host_name(self):
        return self._config['bootstrap-host-name']

    def connect_port(self):
        return self._config['bootstrap-connect-port']
