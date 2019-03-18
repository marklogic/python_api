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
import json
import logging
from marklogic.connection import Connection
from marklogic.models.model import Model
from marklogic.models.host import Host
from marklogic.exceptions import UnexpectedManagementAPIResponse


class LocalCluster(Model):
    """
    The LocalCluster class encapsulates the local cluster.

    For reasons that don't seem obvious today, it's not handled using the same
    marshal and unmarshal approach as other resources. That's probably a bug.
    """
    def __init__(self,connection=None, save_connection=True):
        """
        Create a local cluster.
        """
        self._config = {}
        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic")

    def bootstrap_hosts(self):
        return self._get_config_property('bootstrap-host')

    def read(self, connection=None):
        if connection is None:
            connection = self.connection

        cluster = LocalCluster.lookup(connection)

        if cluster is not None:
            self._config = cluster._config
            self.etag = cluster.etag
            self.name = cluster._config['cluster-name']

        return self

    def view(self, viewname, connection=None):
        if connection is None:
            connection = self.connection

        uri = connection.uri("", properties=None,
                             parameters=["view="+viewname])
        response = connection.get(uri)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def version(self):
        status = self.view("status")
        if status is None:
            return None
        else:
            return status["local-cluster-status"]["version"]

    def update(self, connection=None):
        if connection is None:
            connection = self.connection

        uri = "{0}://{1}:{2}/manage/v2/properties".format(
            connection.protocol, connection.host, connection.management_port)
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)

        # In case we renamed it
        self.name = self._config['cluster-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def restart(self, connection=None):
        if connection is None:
            connection = self.connection

        uri = "{0}://{1}:{2}/manage/v2".format(
            connection.protocol, connection.host, connection.management_port)
        struct = {'operation': 'restart-local-cluster'}
        response = connection.post(uri, payload=struct)
        return self

    def shutdown(self, connection=None):
        if connection is None:
            connection = self.connection

        uri = "{0}://{1}:{2}/manage/v2".format(
            connection.protocol, connection.host, connection.management_port)
        struct = {'operation': 'shutdown-local-cluster'}
        response = connection.post(uri, payload=struct)
        return None

    @classmethod
    def lookup(cls, connection):
        uri = "{0}://{1}:{2}/manage/v2/properties".format(
            connection.protocol, connection.host, connection.management_port)
        response = connection.get(uri)
        if response.status_code == 200:
            result = LocalCluster.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    @classmethod
    def unmarshal(cls, config):
        result = LocalCluster()
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
        struct = {}
        for key in self._config:
            if (key == 'bootstrap-host'):
                jlist = []
                for index in self._config[key]:
                    jlist.append(index._config)
                struct[key] = jlist
            else:
                struct[key] = self._config[key]
        return struct

    def add_host(self, host, connection=None):
        if connection is None:
            connection = self.connection

        if isinstance(host, str):
            host = Host(host)

        xml = host._get_server_config()
        cfgzip = self._post_server_config(xml, connection)

        host_connection = Connection(host.host_name(), connection.auth)
        host._post_cluster_config(cfgzip, host_connection)

    def remove_host(self, host, connection=None):
        if connection is None:
            connection = self.connection

        uri = "{0}://{1}:8001/admin/v1/host-config?remote-host={2}" \
              .format(connection.protocol, connection.host, host)

        response = connection.delete(uri)

    def couple(self, other_cluster, connection=None,
               other_cluster_connection=None):
        if connection is None:
            connection = self.connection
        if other_cluster_connection is None:
            other_cluster_connection = other_cluster.connection

        self.read(connection)
        other_cluster.read(other_cluster_connection)

        uri = "{0}://{1}:{2}/manage/v2/clusters".format(
            connection.protocol, connection.host, connection.management_port)
        struct = other_cluster.marshal()
        response = connection.post(uri, payload=struct)

        uri = "{0}://{1}:{2}/manage/v2/clusters".format(
            other_cluster_connection.protocol,
            other_cluster_connection.host,
            other_cluster_connection.management_port)

        struct = self.marshal()
        response = other_cluster_connection.post(uri, payload=struct)

    def _post_server_config(self, xml, connection):
        """
        Send the server configuration to the a bootstrap host on the
        cluster to which you wish to couple. This is the first half of
        the handshake necessary to join a host to a cluster. The results
        are not intended for introspection.

        :param connection: The connection credentials to use
        :param xml: The XML payload from get_server_config()
        :return: The cluster configuration as a ZIP file.
        """
        uri = "{0}://{1}:8001/admin/v1/cluster-config".format(
            connection.protocol, connection.host)

        struct = {'group': 'Default',
                  'server-config': xml}

        response = connection.post(uri, payload=struct,
                                   content_type='application/x-www-form-urlencoded')

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        return response.content

    # Below this point are machine generated methods for getting
    # and setting atomic values

    def security_version(self):
        """
        The security database version.

        :return: The security-version.
        """
        return self._get_config_property('security-version')

    def cluster_id(self):
        """
        A cluster ID.

        :return: The cluster-id.
        """
        return self._get_config_property('cluster-id')

    def ssl_fips_enabled(self):
        """
        Whether or not SSL FIPS is enabled.

        :return: The ssl-fips-enabled.
        """
        return self._get_config_property('ssl-fips-enabled')

    def set_ssl_fips_enabled(self, value=True):
        """
        Set the ssl-fips-enabled.

        :param value: The ssl-fips-enabled.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('ssl-fips-enabled', value)

    def effective_version(self):
        """
        Software version of a cluster

        :return: The effective-version.
        """
        return self._get_config_property('effective-version')

    def cluster_name(self):
        """
        A cluster name.

        :return: The cluster-name.
        """
        return self._get_config_property('cluster-name')

    def set_cluster_name(self, value):
        """
        Set the cluster-name.

        :param value: The cluster-name.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('cluster-name', value)

    def xdqp_ssl_certificate(self):
        return self._get_config_property('xdqp-ssl-certificate')

    def xdqp_ssl_private_key(self):
        return self._get_config_property('xdqp-ssl-private-key')

    def language_baseline(self):
        return self._get_config_property('language-baseline')

    def opsdirector_log_level(self):
        """
        The OpsDirector log level.

        :return: The log level.
        """
        return self._get_config_property("opsdirector-log-level")

    def set_opsdirector_log_level(self, value):
        """
        Set the OpsDirector log level.

        :param value: The log level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['disabled', 'finest', 'finer', 'fine',
                               'debug', 'config', 'info', 'notice',
                               'warning', 'error', 'critical', 'alert', 'emergency'])
        return self._set_config_property("opsdirector-log-level", value)

    def opsdirector_metering(self):
        """
        The OpsDirector metering level.

        :return: The metering level.
        """
        return self._get_config_property("opsdirector_metering")

    def set_opsdirector_metering(self, value):
        """
        Set the OpsDirector metering level.

        :param value: The metering level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['disabled', 'full', 'aggregates', 'usage-only'])
        return self._set_config_property("opsdirector-metering", value)

    def opsdirector_session_endpoint(self):
        """
        The OpsDirector session endpoint.

        :return: The endpoint.
        """
        return self._get_config_property("opsdirector-session-endpoint")

    def set_opsdirector_session_endpoint(self, value):
        """
        Set the OpsDirector session endpoint.

        :param value: The endpoint.
        :return: The object with the mutated property value.
        """
        # FIXME: Should I test that this is a reasonable http(s) URI?
        return self._set_config_property("opsdirector-session-endpoint", value)

class ForeignCluster(Model):
    """
    The ForeignCluster class encapsulates a foreign cluster.
    """
    def __init__(self,name,connection=None, save_connection=True):
        """
        Create a foreign cluster.
        """
        self._config = {'foreign-cluster-name': name}
        self.name = name
        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic")

    def bootstrap_hosts(self):
        return self._get_config_property('foreign-bootstrap-host')

    def read(self, connection=None):
        if connection is None:
            connection = self.connection

        cluster = ForeignCluster.lookup(connection, self.name)

        if cluster is not None:
            self._config = cluster._config
            self.etag = cluster.etag
            self.name = cluster._config['foreign-cluster-name']

        return self

    def update(self, connection=None):
        if connection is None:
            connection = self.connection

        uri = connection.uri("clusters", self.name)
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)

        # In case we renamed it
        self.name = self._config['foreign-cluster-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    @classmethod
    def list(cls, connection):
        uri = connection.uri("clusters")
        response = connection.get(uri)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            items = response_json['cluster-default-list']['list-items']
            db_count = items['list-count']['value']

            result = []
            if db_count > 0:
                for item in items['list-item']:
                    if item['roleref'] == 'foreign':
                        result.append(item['nameref'])
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    @classmethod
    def lookup(cls, connection, name):
        uri = connection.uri("clusters", name)
        response = connection.get(uri)

        if response.status_code == 200:
            result = ForeignCluster.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    @classmethod
    def unmarshal(cls, config):
        result = ForeignCluster("Temp")
        result._config = config
        result.name = result._config['foreign-cluster-name']

        olist = []
        if 'foreign-bootstrap-host' in result._config:
            for index in result._config['foreign-bootstrap-host']:
                temp = BootstrapHost(index['foreign-host-id'],
                                     index['foreign-host-name'],
                                     index['foreign-connect-port'])
                olist.append(temp)
        result._config['foreign-bootstrap-host'] = olist

        return result

    def marshal(self):
        struct = {}
        for key in self._config:
            if (key == 'foreign-bootstrap-host'):
                jlist = []
                for index in self._config[key]:
                    substruct = {
                        'foreign-host-id': index.host_id(),
                        'foreign-host-name': index.host_name(),
                        'foreign-connect-port': index.connect_port()
                        }
                    jlist.append(substruct)
                struct[key] = jlist
            else:
                struct[key] = self._config[key]

        return struct

    # Below this point are machine generated methods for getting
    # and setting atomic values

    def foreign_cluster_name(self):
        """
        A cluster name.

        :return: The foreign-cluster-name.
        """
        return self._get_config_property('foreign-cluster-name')

    def xdqp_ssl_allow_tls(self):
        """
        true or false

        :return: The xdqp-ssl-allow-tls.
        """
        return self._get_config_property('xdqp-ssl-allow-tls')

    def set_xdqp_ssl_allow_tls(self, value=True):
        """
        Set the xdqp-ssl-allow-tls.

        :param value: The xdqp-ssl-allow-tls.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('xdqp-ssl-allow-tls', value)

    def foreign_protocol(self):
        """
        The protocol for talking to the foreign cluster.

        :return: The foreign-protocol.
        """
        return self._get_config_property('foreign-protocol')

    def set_foreign_protocol(self, value):
        """
        Set the foreign-protocol.

        :param value: The foreign-protocol.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('foreign-protocol', value)

    def xdqp_ssl_allow_sslv3(self):
        """
        true or false

        :return: The xdqp-ssl-allow-sslv3.
        """
        return self._get_config_property('xdqp-ssl-allow-sslv3')

    def set_xdqp_ssl_allow_sslv3(self, value=True):
        """
        Set the xdqp-ssl-allow-sslv3.

        :param value: The xdqp-ssl-allow-sslv3.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('xdqp-ssl-allow-sslv3', value)

    def foreign_cluster_id(self):
        """
        The cluster id.

        :return: The foreign-cluster-id.
        """
        return self._get_config_property('foreign-cluster-id')

    def host_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The host-timeout.
        """
        return self._get_config_property('host-timeout')

    def set_host_timeout(self, value):
        """
        Set the host-timeout.

        :param value: The host-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('host-timeout', value)

    def xdqp_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The xdqp-timeout.
        """
        return self._get_config_property('xdqp-timeout')

    def set_xdqp_timeout(self, value):
        """
        Set the xdqp-timeout.

        :param value: The xdqp-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('xdqp-timeout', value)

    def xdqp_ssl_enabled(self):
        """
        true or false

        :return: The xdqp-ssl-enabled.
        """
        return self._get_config_property('xdqp-ssl-enabled')

    def set_xdqp_ssl_enabled(self, value=True):
        """
        Set the xdqp-ssl-enabled.

        :param value: The xdqp-ssl-enabled.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('xdqp-ssl-enabled', value)

    def xdqp_ssl_ciphers(self):
        """
        The ID of the certificate template in the security database.

        :return: The xdqp-ssl-ciphers.
        """
        return self._get_config_property('xdqp-ssl-ciphers')

    def set_xdqp_ssl_ciphers(self, value):
        """
        Set the xdqp-ssl-ciphers.

        :param value: The xdqp-ssl-ciphers.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('xdqp-ssl-ciphers', value)

class BootstrapHost(Model):
    """
    The BootstrapHost class encapsulates a MarkLogic cluster bootstrap host.
    """
    def __init__(self, host_id, host_name, connect_port):
        self._config = {'bootstrap-host-id': host_id,
                        'bootstrap-host-name': host_name,
                        'bootstrap-connect-port': connect_port}
        self.etag = None
        self.logger = logging.getLogger("marklogic")

    def host_id(self):
        return self._get_config_property('bootstrap-host-id')

    def host_name(self):
        return self._get_config_property('bootstrap-host-name')

    def connect_port(self):
        return self._get_config_property('bootstrap-connect-port')
