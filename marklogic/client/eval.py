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
# Norman Walsh      02/09/2016     Initial development
#

"""
Support the v1/eval endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import
import json, logging
from marklogic.client.exceptions import InvalidAPIRequest
from requests_toolbelt import MultipartDecoder

class Eval:
    """
    The Eval class encapsulates a call to the Client API v1/eval endpoint.
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create an eval object.
        """
        self._config = {}
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.eval")

    def _get(self, name):
        """Internal method to conditionally get a config variable"""
        if name in self._config:
            return self._config[name]
        else:
            return None

    def set_xquery(self, code):
        """Set the XQuery code to evaluate"""
        if 'javascript' in self._config:
            raise InvalidAPIRequest("Cannot specify both xquery and javascript")

        self._config['xquery'] = code
        return self

    def xquery(self):
        """Get the XQuery code to evaluate"""
        return self._get('xquery')

    def set_javascript(self, code):
        """Set the JavaScript code to evaluate"""
        if 'xquery' in self._config:
            raise InvalidAPIRequest("Cannot specify both xquery and javascript")

        self._config['javascript'] = code
        return self

    def javascript(self):
        """Get the JavaScript code to evaluate"""
        return self._get('javascript')

    def set_var(self, name, value):
        """Set a single variable"""
        if 'vars' in self._config:
            vardict = self._config['vars']
        else:
            vardict = {}

        vardict[name] = value

        self._config['vars'] = vardict
        return self

    def set_vars(self, vardict):
        """Set all of the variables.

        The vardict must be a dictionary. The variables defined in the
        dictionary replace all currently defined variables.
        """
        self._config['vars'] = vardict
        return self

    def vars(self):
        """Get the dictionary of defined variables."""
        return self._get('vars')

    def set_database(self, dbname):
        """Set the database."""
        self._config['database'] = dbname
        return self

    def database(self):
        """Get the database"""
        return self._get('database')

    def set_txid(self, txid):
        """Set the transaction ID"""
        self._config['txid'] = txid
        return self

    def txid(self):
        """Get the transaction ID"""
        return self._get('txid')

    def clear(self):
        """Clear the Eval object; return it to its initial state."""
        self._config = {}

    def eval(self, connection=None):
        """Perform the evaluation specified."""
        if connection is None:
            connection = self.connection

        data = {}
        for key in self._config:
            if key is not 'vars':
                data[key] = self._config[key]

        if 'vars' in self._config:
            data['vars'] = json.dumps(self._config['vars'])

        uri = connection.client_uri("eval")
        response = connection.post(uri, payload=data, \
                                       content_type="application/x-www-form-urlencoded", \
                                       accept="multipart/mixed")
        return response

