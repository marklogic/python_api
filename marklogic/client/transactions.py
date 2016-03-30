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
import json, logging, re, sys
from marklogic import MarkLogic
from marklogic.exceptions import UnexpectedManagementAPIResponse
from requests_toolbelt import MultipartDecoder

class Transactions:
    """The Transactions class encapsulates a call to the Client API
    v1/transactions endpoint.
    """
    def __init__(self, connection=None, save_connection=True):
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
        """Internal method to conditionally get a config variable"""
        if name in self._config:
            return self._config[name]
        else:
            return None

    def _set(self, name, value):
        """Internal method to conditionally set a config variable"""
        if name in self._config:
            del self._config[name]
        if value is not None:
            self._config[name] = value
        return self

    def set_name(self, name):
        """Set the transaction name"""
        return self._set('name', name)

    def name(self):
        """Get the transaction name"""
        return self._get('name')

    def set_txid(self, txid):
        """Set the transaction ID"""
        return self._set('txid', txid)

    def txid(self):
        """Get the transaction ID"""
        return self._get('txid')

    def set_timeLimit(self, limit):
        """Set the transaction time limit"""
        return self._set('timeLimit', limit)

    def timeLimit(self):
        """Get the transaction time limit"""
        return self._get('timeLimit')

    def set_database(self, dbname):
        """Set the database"""
        return self._set('database', dbname)

    def database(self):
        """Get the database"""
        return self._get('database')

    def set_format(self, form):
        """
        Set the format parameter for responses.

        If the format is 'json', the accept header will be set to
        application/json, otherwise the accept header will be set to
        application/xml. If you want to specify a different accept
        header, call set_accept() after calling set_format().
        """
        self._set('format', form)
        if form == "json":
            self._config['accept'] = "application/json"
        else:
            self._config['accept'] = "application/xml"
        return self

    def format(self):
        """Get the format"""
        return self._get('format')

    def set_accept(self, accept):
        """Set the accept header"""
        return self._set('accept', accept)

    def accept(self):
        """Get the accept header"""
        return self._get('accept')

    def clear(self):
        """Clear the object; return it to its initial state"""
        self._config = {}
        self._config['accept'] = "application/xml"

    def create(self, connection=None):
        """Create a transaction.

        If successful, the transaction ID will be set in the configuration
        of this object.
        """
        if connection is None:
            connection = self.connection

        fields = []
        for key in ['name', 'database', 'timeLimit']:
            if key in self._config:
                fields.append(key + "=" + str(self._config[key]))

        uri = connection.client_uri("transactions")

        params = "?" + "&".join(fields)

        response = connection.post(uri + params, payload=None, \
                                       content_type="text/plain", \
                                       accept="application/json")

        if response.status_code == 200:
            data = json.loads(response.text)
            self._config['txid'] = data['transaction-status']['transaction-id']

        return response

    def get(self, txid=None, connection=None):
        """Get the properties associated with the transaction."""
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
        """Commit the transaction"""
        return self._result("commit", txid, connection)

    def rollback(self, txid=None, connection=None):
        """Roll back the transaction"""
        return self._result("rollback", txid, connection)

    def max_timeLimit(self, connection=None):
        if connection is None:
            connection = self.connection

        # Work out which appserver we're running against
        # 1. It's usually 'App-Services'
        marklogic = MarkLogic(connection)
        server = marklogic.http_server('App-Services')
        if server.exists() and server.port() == connection.port:
            pass
        else:
            slist = marklogic.http_servers()
            server = None
            while slist and server is None:
                group, name = re.split("\\|", slist.pop())
                try:
                    check = marklogic.http_server(name, group=group)
                    if check.port() == connection.port:
                        server = check
                except UnexpectedManagementAPIResponse:
                    pass
                except:
                    raise

        if (server is not None and server.exists() \
                and server.port() == connection.port):
            return server.max_time_limit()
        else:
            # Oh, heck, just go with a default
            return 600

        sys.exit(1)

    def _result(self, result, txid=None, connection=None):
        """Internal method to commit or rollback a transaction."""
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

        response = connection.post(uri, payload=data, \
                                       accept=self._config['accept'])

        return response
