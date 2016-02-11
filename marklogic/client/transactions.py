# -*- coding: utf-8 -*-
#
# Copyright 2016 MarkLogic Corporation
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
# Norman Walsh      02/10/2016     Initial development
#

"""
Support the v1/transactions endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import
import json, logging, time
from marklogic.connection import Connection
from marklogic.client.exceptions import *
from requests_toolbelt import MultipartDecoder

class Transactions:
    """
    The Transactions class encapsulates a call to the Client API v1/transactions endpoint.
    """
    def __init__(self,connection=None,save_connection=True):
        """
        Create a transactions object.
        """
        self._config = {}
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.transactions")
        self.clear()

    def _get(self, name):
        if name in self._config:
            return self._config[name]
        else:
            return None

    def _set(self, name, value):
        if name in self._config:
            del self._config[name]
        if value is not None:
            self._config[name] = value
        return self

    def set_name(self, name):
        return self._set('name', name)

    def name(self):
        return self._get('name')

    def set_txid(self, txid):
        return self._set('txid', txid)

    def txid(self):
        return self._get('txid')

    def set_timeLimit(self, limit):
        return self._set('timeLimit', limit)

    def timeLimit(self):
        return self._get('timeLimit')

    def set_database(self, dbname):
        return self._set('database', dbname)

    def database(self):
        return self._get('database')

    def set_format(self, form):
        self._set('format', form)
        if form == "json":
            self._config['accept'] = "application/json"
        else:
            self._config['accept'] = "application/xml"
        return self

    def format(self):
        return self._get('format')

    def set_accept(self, accept):
        return self._set('accept', accept)

    def accept(self):
        return self._get('accept')

    def clear(self):
        self._config = {}
        self._config['accept'] = "application/xml"

    def create(self, connection=None):
        if connection is None:
            connection = self.connection

        fields = []
        for key in ['name', 'database']:
            if key in self._config:
                fields.append(key + "=" + self._config[key])

        uri = connection.client_uri("transactions")

        params = "?" + "&".join(fields)

        response = connection.post(uri + params, payload=None, content_type="text/plain",
                                       accept="application/json")

        if response.status_code == 200:
            data = json.loads(response.text)
            self._config['txid'] = data['transaction-status']['transaction-id']

        return response

    def get(self, txid=None, connection=None):
        if connection is None:
            connection = self.connection

        if txid is None:
            txid = self._config['txid']

        data = {}
        for key in ['format', 'database']:
            if key in self._config:
                data[key] = self._config[key]

        uri = connection.client_uri("transactions")
        uri = uri + "/" + txid

        response = connection.get(uri, accept=self._config['accept'])

        return response

    def commit(self, txid=None, connection=None):
        return self._result("commit", txid, connection)

    def rollback(self, txid=None, connection=None):
        return self._result("rollback", txid, connection)

    def _result(self, result, txid=None, connection=None):
        if connection is None:
            connection = self.connection

        if txid is None:
            txid = self._config['txid']

        data = {}
        for key in ['format']:
            if key in self._config:
                data[key] = self._config[key]

        uri = connection.client_uri("transactions")
        uri = uri + "/" + txid + "?result=" + result

        response = connection.post(uri, payload=data, accept=self._config['accept'])

        return response


