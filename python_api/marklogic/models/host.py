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
import requests
import json

class Host:
    """
    The Host class encapsulates a MarkLogic host.
    """
    def __init__(self):
        """
        Create a host.
        """
        self._config = {}

    def host_name(self):
        """
        Returns the host name of the cluster member
        :return: The member host name
        """
        return self._config['host-name']

    def group_name(self):
        """
        The cluster member's group

        :return: Host's Group
        """
        return self._config['group']

    def bind_port(self):
        """
        The bind port of the cluster member

        :return: The host's bind port
        """
        return self._config['bind-port']

    def foreign_bind_port(self):
        """
        The foreign bind port.

        :return: The Host's foreign bind port
        """
        return self._config['foreign-bind-port']

    def zone(self):
        """
        The zone

        :return: The zone
        """
        return self._config['zone']

    def bootstrap_host(self):
        """
        Indicates if this is the bootstrap host

        :return:Bootstrap host indicator
        """
        return self._config['boostrap-host']

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up an individual host within the cluster.

        :param name: The name of the host
        :param connection: A connection to a MarkLogic server
        :return: The host information
        """
        uri = "http://{0}:{1}/manage/v2/hosts/{2}/properties".format(connection.host, connection.management_port,
                                                                     name)
        result = None
        response = requests.get(uri, auth=connection.auth, headers={'accept': 'application/json'})
        if response.status_code == 200:
            result = Host()
            result._config = json.loads(response.text)
        elif response.status_code != 404:
            raise UnexpectedManagementAPIResponse(response.text)
        return result

    @classmethod
    def list(cls, connection):
        """
        Lists the names of hosts available on this cluster.

        :param connection: A connection to a MarkLogic server
        :return: A list of host names
        """
        uri = "http://{0}:{1}/manage/v2/hosts" \
          .format(connection.host, connection.management_port)

        response = requests.get(uri, auth=connection.auth,
                                headers={u'accept': u'application/json'})

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
