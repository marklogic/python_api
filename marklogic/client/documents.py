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
Support the v1/documents endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import
import json, logging, time
from marklogic.connection import Connection
from marklogic.utilities import PropertyLists
from marklogic.client.exceptions import *
from requests_toolbelt import MultipartDecoder

class Documents(PropertyLists):
    """
    The Documents class encapsulates a call to the Client API v1/documents endpoint.
    """
    def __init__(self,connection=None,save_connection=True):
        """
        Create an eval object.
        """
        self._config = {}
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.documents")

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

    def set_uris(self, uris):
        return self.set_property_list('uri', uris)

    def set_uri(self, uri):
        self._config['uri'] = []
        if uri is not None:
            self._config['uri'].append(uri)
        return self

    def add_uri(self, uri):
        return self.add_to_property_list('uri', uri)

    def uris(self):
        return self._get_config_property('uri')

    def set_database(self, dbname):
        return self._set('database', dbname)

    def database(self):
        return self._get('database')

    def set_forest(self, forest):
        return self._set('forest-name', forest)

    def forest(self):
        return self._get('forest')

    def set_categories(self, cats):
        return self.set_property_list('category', cats)

    def set_category(self, cat):
        self._config['category'] = []
        if cat is not None:
            self._config['category'].append(cat)
        return self

    def add_category(self, cat):
        return self.add_to_property_list('category', cat)

    def categories(self):
        return self._get_config_property('category')

    def set_format(self, form):
        self._set('format', form)
        if form == "json":
            self._config['accept'] = "application/json"
        else:
            self._config['accept'] = "application/xml"
        return self

    def format(self):
        return self._get('format')

    def set_transform(self, transform):
        return self._set('transform', transform)

    def transform(self):
        return self._get('transform')

    def set_transform_param(self, name, value):
        self._config['transparam'] = []
        return self.add_transform_param(name, value)

    def set_transform_params(self, tuples):
        self._config['transparam'] = []
        if tuples is not None:
            self.add_transform_params(tuples)
        return self

    def add_transform_param(self, name, value):
        self._config['transparam'].append("trans:" + name + "=" + value)
        return self

    def add_transform_params(self, tuples):
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_transform_param(self, pair[0], pair[1])
        return self

    def transform_param(self, name):
        if 'transparam' in self._config:
            key = "trans:" + name + "="
            for item in self._config['transparam']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def transform_params(self):
        params = []
        if 'transparam' in self._config:
            for item in self._config['transparam']:
                params.append(tuple(item[6:].split('=')))
            return params
        else:
            return None

    def set_txid(self, txid):
        return self._set('txid', txid)

    def txid(self):
        return self._get('txid')

    def set_accept(self, accept):
        return self._set('accept', accept)

    def accept(self):
        return self._get('accept')

    def set_content_type(self, content_type):
        return self._set('content-type', content_type)

    def content_type(self):
        return self._get('content-type')

    def if_none_match(self, version):
        raise UnsupportedOperationException("Not implemented yet")

    def range(self, start=None, end=None):
        raise UnsupportedOperationException("Not implemented yet")

    def set_quality(self, quality):
        return self._set('quality', quality)

    def quality(self):
        return self._get('quality')

    def set_permission(self, role, value):
        self._config['permission'] = []
        return self.add_permission(role, value)

    def set_permissions(self, tuples):
        self._config['permission'] = []
        if tuples is not None:
            self.add_permissions(tuples)
        return self

    def add_permission(self, role, value):
        self._config['permission'].append("perm:" + role + "=" + value)
        return self

    def add_permissions(self, tuples):
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_permission(self, pair[0], pair[1])
        return self

    def permission(self, role):
        if 'permission' in self._config:
            key = "perm:" + role + "="
            for item in self._config['permission']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def permissions(self):
        perms = []
        if 'permission' in self._config:
            for item in self._config['permission']:
                perms.append(tuple(item[5:].split('=')))
            return perms
        else:
            return None

    def set_property(self, name, value):
        self._config['property'] = []
        return self.add_property(name, value)

    def set_properties(self, tuples):
        self._config['property'] = []
        if tuples is not None:
            self.add_properties(tuples)
        return self

    def add_property(self, name, value):
        self._config['property'].append("prop:" + name + "=" + value)
        return self

    def add_properties(self, tuples):
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_property(self, pair[0], pair[1])
        return self

    def property(self, role):
        if 'property' in self._config:
            key = "prop:" + role + "="
            for item in self._config['property']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def properties(self):
        props = []
        if 'property' in self._config:
            for item in self._config['property']:
                props.append(tuple(item[5:].split('=')))
            return props
        else:
            return None

    def set_extract(self, value):
        return self._set('extract', value)

    def extract(self):
        return self._get('extract')

    def set_repair(self, value):
        return self._set('repair', value)

    def repair(self):
        return self._get('repair')

    def set_lang(self, language):
        return self._set('lang', language)

    def lang(self):
        return self._get('lang')

    def set_temporal_collection(self, collection):
        return self._set('temporal-collection', collection)

    def temporal_collection(self):
        return self._get('temporal-collection')

    def set_system_time(self, time):
        return self._set('system-time', time)

    def system_time(self):
        return self._get('system-time')

    def clear(self):
        self._config = {}
        self._config['uri'] = []
        self._config['category'] = []
        self._config['transparam'] = []
        self._config['permission'] = []
        self._config['property'] = []
        self._config['accept'] = "application/xml"
        self._config['content-type'] = "application/xml"

    def _plist(self, propname):
        param = ""

        if propname in self._config:
            for prop in self._config[propname]:
                param = param + "&" + propname + "=" + prop

        return param

    def get(self, uri=None, connection=None):
        if connection is None:
            connection = self.connection

        if uri is None:
            uris = []
            for uri in self._config['uri']:
                uris.append("uri=" + uri)
        else:
            uris = ["uri=" + uri]

        params = "?" + "&".join(uris);

        for key in ['database', 'format', 'transform', 'txid']:
            if key in self._config:
                params = params + "&" + key + "=" + self._config[key]

        params = params + self._plist("category")

        if self._config['transparam']:
            params = params + "&" + "&".join(self._config['transparam'])

        uri = connection.client_uri("documents")

        response = connection.get(uri + params, accept=self._config['accept'])
        return response

    def put(self, data, uri=None, connection=None):
        if connection is None:
            connection = self.connection

        if uri is None:
            if len(self._config['uri']) != 1:
                raise InvalidAPIRequest("Must PUT with exactly one URI")
            uri = self._config['uri'][0]

        params = "?uri=" + uri

        for key in ['database', 'format', 'quality', 'extract', 'repair',
                        'transform', 'forest-name', 'txid', 'lang',
                        'temporal-collection', 'system-time']:
            if key in self._config:
                params = params + "&" + key + "=" + self._config[key]

        params = params + self._plist("category")
        params = params + self._plist("collection")

        if self._config['permission']:
            params = params + "&" + "&".join(self._config['permission'])

        if self._config['property']:
            params = params + "&" + "&".join(self._config['property'])

        if self._config['transparam']:
            params = params + "&" + "&".join(self._config['transparam'])

        uri = connection.client_uri("documents")

        response = connection.put(uri + params, payload=data,
                                      content_type=self._config['content-type'],
                                      accept=self._config['accept'])
        return response

    def delete(self, uri=None, connection=None):
        if connection is None:
            connection = self.connection

        if uri is None:
            uris = []
            for uri in self._config['uri']:
                uris.append("uri=" + uri)
        else:
            uris = ["uri=" + uri]

        params = "?" + "&".join(uris);

        for key in ['database', 'txid', 'temporal-collection', 'system-time']:
            if key in self._config:
                params = params + "&" + key + "=" + self._config[key]

        params = params + self._plist("category")

        uri = connection.client_uri("documents")

        response = connection.delete(uri + params)

        return response
