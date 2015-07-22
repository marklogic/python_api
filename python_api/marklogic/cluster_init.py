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
# Norman Walsh      15 July 2015   Initial development
#

"""
Functions for initializing clusters
"""

from __future__ import unicode_literals, print_function, absolute_import
import requests
from requests.auth import HTTPDigestAuth
import json
import logging
from marklogic.models.connection import Connection
from marklogic.models.host import Host
from marklogic.models.utilities.exceptions import *

class ClusterInit:
    """
    The ClusterInit class provides methods for initializing a cluster.
    """
    def __init__(self):
        """
        Create a configuration object
        """
        self.logger = logging.getLogger("marklogic")

    def init(self,host):
        conn = Connection(host, None)

        uri = "http://{0}:8001/admin/v1/init".format(conn.host)

        response = requests.post(uri, auth=conn.auth,
                                 headers={'content-type':
                                          'application/x-www-form-urlencoded',
                                          'accept':
                                          'application/json'})

        if response.status_code == 401:
            raise UnauthorizedAPIRequest(response.text)

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        data = json.loads(response.text)
        Host.wait_for_restart(conn, data["restart"]["last-startup"][0]["value"])

    def instance_admin(self,host,realm,admin,password):
        conn = Connection(host, None)

        payload = {
            'admin-username': admin,
            'admin-password': password,
            'realm': realm
            }

        uri = "http://{0}:8001/admin/v1/instance-admin".format(conn.host)

        response = requests.post(uri, json=payload,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        # From now on connections require auth...
        conn = Connection(host, HTTPDigestAuth(admin, password))
        data = json.loads(response.text)
        Host.wait_for_restart(conn, data["restart"]["last-startup"][0]["value"])

    def get_server_config(self,conn):
        uri = "http://{0}:8001/admin/v1/server-config".format(conn.host)

        response = requests.get(uri)

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        return response.text # this is always XML

    def post_server_config(self,conn,xml):
        uri = "http://{0}:8001/admin/v1/cluster-config".format(conn.host)

        payload = { 'group': 'Default',
                    'server-config': xml }

        response = requests.post(uri, data=payload, auth=conn.auth,
                                 headers={'content-type': 'application/x-www-form-urlencoded',
                                          'accept': 'application/json'})

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        return response.content

    def post_cluster_config(self,conn,cfgzip):
        uri = "http://{0}:8001/admin/v1/cluster-config".format(conn.host)

        response = requests.post(uri, data=cfgzip, auth=conn.auth,
                                 headers={'content-type': 'application/zip',
                                          'accept': 'application/json'})

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        data = json.loads(response.text)
        Host.wait_for_restart(conn, data["restart"]["last-startup"][0]["value"])


    def rename_cluster(self,conn,name):
        uri = "http://{0}:8002/manage/v2/properties".format(conn.host)
        payload = {'cluster-name': name}

        response = requests.put(uri, json=payload, auth=conn.auth,
                                headers={'content-type': 'application/json',
                                         'accept': 'application/json'})

        if response.status_code != 204:
            raise UnexpectedManagementAPIResponse(response.text)
