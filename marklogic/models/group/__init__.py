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
# Norman Walsh      08/09/2015     Initial development
#

"""
Class for manipulating MarkLogic groups
"""

from __future__ import unicode_literals, print_function, absolute_import

import json, logging
import marklogic.exceptions
from marklogic.utilities import PropertyLists
from marklogic.models.model import Model
from marklogic.models.host import Host
from marklogic.models.group.audit import Audit, AuditEvent, AuditRestriction
from marklogic.models.group.schema import Schema

class Group(Model, PropertyLists):
    """
    The Group class encapsulates a MarkLogic group.  It provides
    methods to set/get group attributes.  The use of methods will
    allow IDEs with tooling to provide auto-completion hints.
    """
    def __init__(self, name, connection=None, save_connection=True):
        self._config = {}
        self._config['group-name'] = name
        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.name = name

    def events(self):
        return self.get_property_list('event')

    def set_events(self, events):
        return self.set_property_list('event', events, str)

    def add_event(self, event):
        return self.add_to_property_list('event', event, str)

    def remove_event(self, event):
        return self.remove_from_property_list('event', event, str)

    def marshal(self):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = {}
        for key in self._config:
            if key == 'audit':
                substruct = {}
                audit = self._config[key]._config
                for prop in audit:
                    if prop == 'audit-event':
                        events = []
                        for e in audit[prop]:
                            events.append(e._config)
                        substruct[prop] = events
                    elif prop == 'audit-restriction':
                        restr = []
                        for r in audit[prop]:
                            restr.append(r._config)
                        substruct[prop] = restr
                    else:
                        substruct[prop] = audit[prop]
                struct[key] = substruct
            elif key == 'schema':
                olist = []
                for schema in self._config[key]:
                    olist.append(schema._config)
                struct[key] = olist
            else:
                struct[key] = self._config[key]

        return struct

    @classmethod
    def unmarshal(cls, config,
                  connection=None, save_connection=True):
        """
        Construct a new group from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed Group object with the specified properties.
        """
        result = Group("temp", connection=connection,
                       save_connection=save_connection)
        result._config = config
        result.name = config['group-name']
        result.etag = None

        logger = logging.getLogger("marklogic")

        # This long, explicit approach may be somewhat inefficient, but it
        # catches the case where a new, unhandled database property arises.
        # The atomic list are properties that have values that are either
        # atomic values or lists of atomic values.

        atomic = {'background-io-limit',
                  'cache-sizing',
                  'compressed-tree-cache-partitions',
                  'compressed-tree-cache-size',
                  'compressed-tree-read-size', 'events-activated',
                  'expanded-tree-cache-partitions',
                  'expanded-tree-cache-size', 'failover-enable',
                  'file-log-level', 'group-name',
                  'host-initial-timeout', 'host-timeout',
                  'http-timeout', 'http-user-agent', 'keep-log-files',
                  'list-cache-partitions', 'list-cache-size',
                  'metering-enabled', 'meters-database',
                  'module-cache-timeout',
                  'performance-metering-enabled',
                  'performance-metering-period',
                  'performance-metering-retain-daily',
                  'performance-metering-retain-hourly',
                  'performance-metering-retain-raw', 'retry-timeout',
                  'rotate-log-files', 's3-domain', 's3-protocol', 's3-proxy',
                  's3-server-side-encryption', 's3-server-side-encryption-kms-key',
                  'azure-storage-proxy', 'security-database',
                  'smtp-relay', 'smtp-timeout', 'system-log-level',
                  'triple-cache-partitions', 'triple-cache-size',
                  'triple-cache-timeout',
                  'triple-value-cache-partitions',
                  'triple-value-cache-size',
                  'triple-value-cache-timeout',
                  'xdqp-ssl-allow-sslv3', 'xdqp-ssl-allow-tls',
                  'xdqp-ssl-ciphers', 'xdqp-ssl-enabled',
                  'xdqp-timeout', 'telemetry-config',
                  'telemetry-log-level', 'telemetry-metering',
                  'telemetry-session-endpoint', 'telemetry-proxy',
                  'xdqp-ssl-disable-sslv3', 'xdqp-ssl-disable-tlsv1',
                  'xdqp-ssl-disable-tlsv1-1', 'xdqp-ssl-disable-tlsv1-2'
                  }

        for key in result._config:
            olist = []

            if key in atomic:
                pass
            elif key == 'audit':
                audit = result._config[key]
                enabled = None
                keep = None
                rotate = None
                events = []
                restrictions = []
                for prop in audit:
                    if prop == 'audit-enabled':
                        enabled = audit[prop]
                    elif prop == 'keep-audit-files':
                        keep = audit[prop]
                    elif prop == 'rotate-audit-files':
                        rotate = audit[prop]
                    elif prop == 'audit-event':
                        for e in audit[prop]:
                            event = AuditEvent(e['audit-event-name'],
                                               e['audit-event-enabled'])
                            events.append(event)
                    elif prop == 'audit-restriction':
                        for r in audit[prop]:
                            rest = AuditRestriction(r['audit-restriction-name'],
                                                    r['audit-restriction-type'],
                                                    r['audit-restriction-items'])
                            restrictions.append(rest)
                    else:
                        logger.warning("Unexpected audit property: " + prop)
                audit = Audit(enabled, keep, rotate, events, restrictions)
                result._config[key] = audit
            elif key == 'event':
                pass
            elif key == 'schema':
                schemas = []
                for s in result._config[key]:
                    schema = Schema(s['namespace-uri'], s['schema-location'])
                    schemas.append(schema)
                result._config[key] = schemas
            else:
                logger.warning("Unexpected group property: " + key)

        return result

    def exists(self, connection=None):
        """
        Checks to see if the user exists on the server.

        :param connection: The connection to a MarkLogic server
        :return: True if the user exists
        """
        if connection is None:
            connection = self.connection

        group = Group.lookup(connection, self.group_name())
        return group is not None

    def create(self, connection=None):
        """
        Creates the Group on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Group object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("groups")
        struct = self.marshal()
        response = connection.post(uri, payload=struct)
        return self

    def read(self, connection=None):
        """
        Loads the Group from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The Group object
        """
        if connection is None:
            connection = self.connection

        group = Group.lookup(connection, self._config['group-name'])
        if group is None:
            return None
        else:
            self._config = group._config
            self.etag = group.etag
            return self

    def update(self, connection=None):
        """
        Updates the Group on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Group object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("groups", self.name)
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)

        self.name = self._config['group-name']
        if 'etag' in response.headers:
            self.etag = response.headers['etag']

        return self

    def delete(self, connection=None):
        """
        Deletes the Group from the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Group object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("groups", self.name, properties=None)
        response = connection.delete(uri, etag=self.etag)
        return self

    @classmethod
    def list(cls, connection):
        """
        List all the group names.

        :param connection: The connection to a MarkLogic server
        :return: A list of group names
        """

        uri = connection.uri("groups")
        response = connection.get(uri)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['group-default-list']['list-items']['list-item']:
            results.append(item['nameref'])

        return results

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up an group.

        :param name: The name of the group
        :param connection: The connection to the MarkLogic database
        :return: The group
        """
        uri = connection.uri("groups", name)
        response = connection.get(uri)

        if response.status_code == 200:
            result = Group.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    # Below this point are machine generated methods for getting
    # and setting atomic values

    def compressed_tree_read_size(self):
        """
        An integer amount for block sizes in kilobytes, min 8, max 16384.

        :return: The compressed-tree-read-size.
        """
        return self._get_config_property('compressed-tree-read-size')

    def set_compressed_tree_read_size(self, value):
        """
        Set the compressed-tree-read-size.

        :param value: The compressed-tree-read-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 16384, 'min': 8})
        return self._set_config_property('compressed-tree-read-size', value)

    def performance_metering_retain_hourly(self):
        """
        An integer amount of days

        :return: The performance-metering-retain-hourly.
        """
        return self._get_config_property('performance-metering-retain-hourly')

    def set_performance_metering_retain_hourly(self, value):
        """
        Set the performance-metering-retain-hourly.

        :param value: The performance-metering-retain-hourly.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': None, 'min': 1})
        return self._set_config_property('performance-metering-retain-hourly', value)

    def expanded_tree_cache_size(self):
        """
        An integer amount of system memory in megabytes, min 1, max 73728.

        :return: The expanded-tree-cache-size.
        """
        return self._get_config_property('expanded-tree-cache-size')

    def set_expanded_tree_cache_size(self, value):
        """
        Set the expanded-tree-cache-size.

        :param value: The expanded-tree-cache-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 73728, 'min': 1})
        return self._set_config_property('expanded-tree-cache-size', value)

    def metering_enabled(self):
        """
        true or false

        :return: The metering-enabled value.
        """
        return self._get_config_property('metering-enabled')

    def set_metering_enabled(self, value=True):
        """
        Set metering-enabled.

        :param value: The metering-enabled.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('metering-enabled', value)

    def telemetry_config(self):
        """
        The Telemetry config level: disabled, frequent, or infrequent.

        :return: The config level.
        """
        return self._get_config_property("telemetry-config")

    def set_telemetry_config(self, value):
        """
        Set the Telemetry config level: disabled, frequent, or infrequent.

        :param value: The config level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['disabled', 'frequent', 'infrequent'])
        return self._set_config_property('telemetry-config', value)

    def telemetry_log_level(self):
        """
        The Telemetry log level.

        :return: The log level.
        """
        return self._get_config_property("telemetry-log-level")

    def set_telemetry_log_level(self, value):
        """
        Set the Telemetry log level.

        :param value: The log level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['disabled', 'finest', 'finer', 'fine',
                               'debug', 'config', 'info', 'notice',
                               'warning', 'error', 'critical', 'alert', 'emergency'])
        return self._set_config_property("telemetry-log-level", value)

    def telemetry_metering(self):
        """
        The Telemetry metering level.

        :return: The metering level.
        """
        return self._get_config_property("telemetry_metering")

    def set_telemetry_metering(self, value):
        """
        Set the Telemetry metering level.

        :param value: The metering level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['disabled', 'full', 'aggregates', 'usage-only'])
        return self._set_config_property("telemetry-metering", value)

    def telemetry_session_endpoint(self):
        """
        The Telemetry session endpoint.

        :return: The endpoint.
        """
        return self._get_config_property("telemetry-session-endpoint")

    def set_telemetry_session_endpoint(self, value):
        """
        Set the Telemetry session endpoint.

        :param value: The endpoint.
        :return: The object with the mutated property value.
        """
        # FIXME: Should I test that this is a reasonable http(s) URI?
        return self._set_config_property("telemetry-session-endpoint", value)

    def telemetry_proxy(self):
        """
        The Telemetry proxy setting.

        :return: The proxy setting.
        """
        return self._get_config_property("telemetry-proxy")

    def set_telemetry_proxy(self, value):
        """
        Set the Telemetry proxy setting.

        :param value: The proxy setting.
        :return: The object with the mutated property value.
        """
        return self._set_config_property("telemetry-proxy", value)

    def cache_sizing(self):
        """
        The cache sizing property.

        :return: The cache sizing setting.
        """
        return self._get_config_property("cache-sizing")

    def set_cache_sizing(self, value):
        """
        Set the cache sizing value.

        :param value: The cache sizing.
        :return: The object with the mutated property value.
        """
        # FIXME: check that the value is reasonable
        return self._set_config_property("cache-sizing", value)

    def triple_cache_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The triple-cache-timeout.
        """
        return self._get_config_property('triple-cache-timeout')

    def set_triple_cache_timeout(self, value):
        """
        Set the triple-cache-timeout.

        :param value: The triple-cache-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('triple-cache-timeout', value)

    def security_database(self):
        """
        The name of the security database.

        :return: The security-database.
        """
        return self._get_config_property('security-database')

    def set_security_database(self, value):
        """
        Set the security-database.

        :param value: The security-database.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('security-database', value)

    def module_cache_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The module-cache-timeout.
        """
        return self._get_config_property('module-cache-timeout')

    def set_module_cache_timeout(self, value):
        """
        Set the module-cache-timeout.

        :param value: The module-cache-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('module-cache-timeout', value)

    def performance_metering_retain_raw(self):
        """
        An integer amount of days

        :return: The performance-metering-retain-raw.
        """
        return self._get_config_property('performance-metering-retain-raw')

    def set_performance_metering_retain_raw(self, value):
        """
        Set the performance-metering-retain-raw.

        :param value: The performance-metering-retain-raw.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': None, 'min': 1})
        return self._set_config_property('performance-metering-retain-raw', value)

    def performance_metering_period(self):
        """
        An integer amount of seconds

        :return: The performance-metering-period.
        """
        return self._get_config_property('performance-metering-period')

    def set_performance_metering_period(self, value):
        """
        Set the performance-metering-period.

        :param value: The performance-metering-period.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': None, 'min': 1})
        return self._set_config_property('performance-metering-period', value)

    def background_io_limit(self):
        """
        An I/O limit in megabytes per second (min 0, no maximum; 0 means unlimited).

        :return: The background-io-limit.
        """
        return self._get_config_property('background-io-limit')

    def set_background_io_limit(self, value):
        """
        Set the background-io-limit.

        :param value: The background-io-limit.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': None, 'min': 0})
        return self._set_config_property('background-io-limit', value)

    def file_log_level(self):
        """
        emergency, alert, critical, error, warning, notice, info, config, debug, fine, finer, or finest

        :return: The file-log-level.
        """
        return self._get_config_property('file-log-level')

    def set_file_log_level(self, value):
        """
        Set the file-log-level.

        :param value: The file-log-level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['finest', 'finer', 'fine', 'debug', 'config', 'info', 'notice', 'warning', 'error', 'critical', 'alert', 'emergency'])
        return self._set_config_property('file-log-level', value)

    def meters_database(self):
        """
        The name of the meters database

        :return: The meters-database.
        """
        return self._get_config_property('meters-database')

    def set_meters_database(self, value):
        """
        Set the meters-database.

        :param value: The meters-database.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('meters-database', value)

    def list_cache_partitions(self):
        """
        An integer number of memory partitions, min 1, max 32.

        :return: The list-cache-partitions.
        """
        return self._get_config_property('list-cache-partitions')

    def set_list_cache_partitions(self, value):
        """
        Set the list-cache-partitions.

        :param value: The list-cache-partitions.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 32, 'min': 1})
        return self._set_config_property('list-cache-partitions', value)

    def s3_protocol(self):
        """
        http or https

        :return: The s3-protocol.
        """
        return self._get_config_property('s3-protocol')

    def set_s3_protocol(self, value):
        """
        Set the s3-protocol.

        :param value: The s3-protocol.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['http', 'https'])
        return self._set_config_property('s3-protocol', value)

    def s3_proxy(self):
        """
        The S3 proxy.

        :return: The s3-proxy.
        """
        return self._get_config_property('s3-proxy')

    def set_s3_proxy(self, value):
        """
        Set the s3-proxy.

        :param value: The s3-proxy.
        :return: The object with the mutated property value.
        """
        return self._set_config_property('s3-proxy', value)

    def azure_storage_proxy(self):
        """
        The Azure storage proxy.

        :return: The azure-storage-proxy.
        """
        return self._get_config_property('azure-storage-proxy')

    def set_azure_storage_proxy(self, value):
        """
        Set the Azure storage proxy.

        :param value: The azure-storage-proxy.
        :return: The object with the mutated property value.
        """
        return self._set_config_property('azure-storage-proxy', value)

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

    def performance_metering_retain_daily(self):
        """
        An integer amount of days

        :return: The performance-metering-retain-daily.
        """
        return self._get_config_property('performance-metering-retain-daily')

    def set_performance_metering_retain_daily(self, value):
        """
        Set the performance-metering-retain-daily.

        :param value: The performance-metering-retain-daily.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': None, 'min': 1})
        return self._set_config_property('performance-metering-retain-daily', value)

    def http_user_agent(self):
        """
        An HTTP User-agent string.

        :return: The http-user-agent.
        """
        return self._get_config_property('http-user-agent')

    def set_http_user_agent(self, value):
        """
        Set the http-user-agent.

        :param value: The http-user-agent.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('http-user-agent', value)

    def compressed_tree_cache_size(self):
        """
        An integer amount of system memory in megabytes, min 1, max 73728.

        :return: The compressed-tree-cache-size.
        """
        return self._get_config_property('compressed-tree-cache-size')

    def set_compressed_tree_cache_size(self, value):
        """
        Set the compressed-tree-cache-size.

        :param value: The compressed-tree-cache-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 73728, 'min': 1})
        return self._set_config_property('compressed-tree-cache-size', value)

    def rotate_log_files(self):
        """
        never, daily, saturday, sunday, monday, or monthly

        :return: The rotate-log-files.
        """
        return self._get_config_property('rotate-log-files')

    def set_rotate_log_files(self, value):
        """
        Set the rotate-log-files.

        :param value: The rotate-log-files.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['never', 'daily', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'monthly'])
        return self._set_config_property('rotate-log-files', value)

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

    def group_name(self):
        """
        The name of a group.

        :return: The group-name.
        """
        return self._get_config_property('group-name')

    def set_group_name(self, value):
        """
        Set the group-name.

        :param value: The group-name.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('group-name', value)

    def triple_cache_partitions(self):
        """
        An integer number of memory partitions, min 1, max 32.

        :return: The triple-cache-partitions.
        """
        return self._get_config_property('triple-cache-partitions')

    def set_triple_cache_partitions(self, value):
        """
        Set the triple-cache-partitions.

        :param value: The triple-cache-partitions.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 32, 'min': 1})
        return self._set_config_property('triple-cache-partitions', value)

    def performance_metering_enabled(self):
        """
        true or false

        :return: The performance-metering-enabled.
        """
        return self._get_config_property('performance-metering-enabled')

    def set_performance_metering_enabled(self, value=True):
        """
        Set the performance-metering-enabled.

        :param value: The performance-metering-enabled.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('performance-metering-enabled', value)

    def triple_value_cache_partitions(self):
        """
        An integer number of memory partitions, min 1, max 32.

        :return: The triple-value-cache-partitions.
        """
        return self._get_config_property('triple-value-cache-partitions')

    def set_triple_value_cache_partitions(self, value):
        """
        Set the triple-value-cache-partitions.

        :param value: The triple-value-cache-partitions.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 32, 'min': 1})
        return self._set_config_property('triple-value-cache-partitions', value)

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

    def compressed_tree_cache_partitions(self):
        """
        An integer number of memory partitions, min 1, max 32.

        :return: The compressed-tree-cache-partitions.
        """
        return self._get_config_property('compressed-tree-cache-partitions')

    def set_compressed_tree_cache_partitions(self, value):
        """
        Set the compressed-tree-cache-partitions.

        :param value: The compressed-tree-cache-partitions.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 32, 'min': 1})
        return self._set_config_property('compressed-tree-cache-partitions', value)

    def xdqp_ssl_ciphers(self):
        """
        The id of the certificate template in the security database.

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

    def events_activated(self):
        """
        true or false

        :return: The events-activated.
        """
        return self._get_config_property('events-activated')

    def set_events_activated(self, value=True):
        """
        Set the events-activated.

        :param value: The events-activated.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('events-activated', value)

    def expanded_tree_cache_partitions(self):
        """
        An integer number of memory partitions, min 1, max 32.

        :return: The expanded-tree-cache-partitions.
        """
        return self._get_config_property('expanded-tree-cache-partitions')

    def set_expanded_tree_cache_partitions(self, value):
        """
        Set the expanded-tree-cache-partitions.

        :param value: The expanded-tree-cache-partitions.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 32, 'min': 1})
        return self._set_config_property('expanded-tree-cache-partitions', value)

    def keep_log_files(self):
        """
        An integer number of log files, min 1, max 365.

        :return: The keep-log-files.
        """
        return self._get_config_property('keep-log-files')

    def set_keep_log_files(self, value):
        """
        Set the keep-log-files.

        :param value: The keep-log-files.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 365, 'min': 1})
        return self._set_config_property('keep-log-files', value)

    def smtp_relay(self):
        """
        A hostname.

        :return: The smtp-relay.
        """
        return self._get_config_property('smtp-relay')

    def set_smtp_relay(self, value):
        """
        Set the smtp-relay.

        :param value: The smtp-relay.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('smtp-relay', value)

    def http_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The http-timeout.
        """
        return self._get_config_property('http-timeout')

    def set_http_timeout(self, value):
        """
        Set the http-timeout.

        :param value: The http-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('http-timeout', value)

    def triple_value_cache_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The triple-value-cache-timeout.
        """
        return self._get_config_property('triple-value-cache-timeout')

    def set_triple_value_cache_timeout(self, value):
        """
        Set the triple-value-cache-timeout.

        :param value: The triple-value-cache-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('triple-value-cache-timeout', value)

    def s3_domain(self):
        """
        An internet domain name.

        :return: The s3-domain.
        """
        return self._get_config_property('s3-domain')

    def set_s3_domain(self, value):
        """
        Set the s3-domain.

        :param value: The s3-domain.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('s3-domain', value)

    def triple_cache_size(self):
        """
        An integer amount of system memory in megabytes, min 1, max 73728.

        :return: The triple-cache-size.
        """
        return self._get_config_property('triple-cache-size')

    def set_triple_cache_size(self, value):
        """
        Set the triple-cache-size.

        :param value: The triple-cache-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 73728, 'min': 1})
        return self._set_config_property('triple-cache-size', value)

    def system_log_level(self):
        """
        emergency, alert, critical, error, warning, notice, info, config, debug, fine, finer, or finest

        :return: The system-log-level.
        """
        return self._get_config_property('system-log-level')

    def set_system_log_level(self, value):
        """
        Set the system-log-level.

        :param value: The system-log-level.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['finest', 'finer', 'fine', 'debug', 'config', 'info', 'notice', 'warning', 'error', 'critical', 'alert', 'emergency'])
        return self._set_config_property('system-log-level', value)

    def s3_server_side_encryption(self):
        """
        none or aes256

        :return: The s3-server-side-encryption.
        """
        return self._get_config_property('s3-server-side-encryption')

    def set_s3_server_side_encryption(self, value):
        """
        Set the s3-server-side-encryption.

        :param value: The s3-server-side-encryption.
        :return: The object with the mutated property value.
        """
        self._validate(value, ['none', 'aes256'])
        return self._set_config_property('s3-server-side-encryption', value)

    def s3_server_side_encryption_kms_key(self):
        """
        The KMS encryption key.

        :return: The s3-server-side-encryption KMS key.
        """
        return self._get_config_property('s3-server-side-encryption-kms-key')

    def set_s3_server_side_encryption_kms_key(self, value):
        """
        Set the s3-server-side-encryption KMS key.

        :param value: The s3-server-side-encryption KMS key.
        :return: The object with the mutated property value.
        """
        return self._set_config_property('s3-server-side-encryption-kms-key', value)

    def host_initial_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The host-initial-timeout.
        """
        return self._get_config_property('host-initial-timeout')

    def set_host_initial_timeout(self, value):
        """
        Set the host-initial-timeout.

        :param value: The host-initial-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('host-initial-timeout', value)

    def list_cache_size(self):
        """
        An integer amount of system memory in megabytes, min 1, max 73728.

        :return: The list-cache-size.
        """
        return self._get_config_property('list-cache-size')

    def set_list_cache_size(self, value):
        """
        Set the list-cache-size.

        :param value: The list-cache-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 73728, 'min': 1})
        return self._set_config_property('list-cache-size', value)

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

    def failover_enable(self):
        """
        true or false

        :return: The failover-enable.
        """
        return self._get_config_property('failover-enable')

    def set_failover_enable(self, value=True):
        """
        Set the failover-enable.

        :param value: The failover-enable.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'boolean')
        return self._set_config_property('failover-enable', value)

    def triple_value_cache_size(self):
        """
        An integer amount of system memory in megabytes, min 1, max 73728.

        :return: The triple-value-cache-size.
        """
        return self._get_config_property('triple-value-cache-size')

    def set_triple_value_cache_size(self, value):
        """
        Set the triple-value-cache-size.

        :param value: The triple-value-cache-size.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 73728, 'min': 1})
        return self._set_config_property('triple-value-cache-size', value)

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

    def smtp_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The smtp-timeout.
        """
        return self._get_config_property('smtp-timeout')

    def set_smtp_timeout(self, value):
        """
        Set the smtp-timeout.

        :param value: The smtp-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('smtp-timeout', value)

    def retry_timeout(self):
        """
        An integer number of seconds, min 0, max 4294967295.

        :return: The retry-timeout.
        """
        return self._get_config_property('retry-timeout')

    def set_retry_timeout(self, value):
        """
        Set the retry-timeout.

        :param value: The retry-timeout.
        :return: The object with the mutated property value.
        """
        self._validate(value, {'max': 4294967295, 'min': 0})
        return self._set_config_property('retry-timeout', value)
