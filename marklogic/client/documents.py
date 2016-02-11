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
import logging
from marklogic.utilities import PropertyLists
from marklogic.client.exceptions import InvalidAPIRequest, UnsupportedOperation

class Documents(PropertyLists):
    """
    The Documents class encapsulates a call to the Client API v1/documents
    endpoint.
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
        self.logger = logging.getLogger("marklogic.client.documents")

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

    def set_uris(self, uris):
        """Set the document URIs to a list of URI strings"""
        return self.set_property_list('uri', uris)

    def set_uri(self, uri):
        """Set the document URIs to a single URI string"""
        self._config['uri'] = []
        if uri is not None:
            self._config['uri'].append(uri)
        return self

    def add_uri(self, uri):
        """Add a single URI to the list of document URIs"""
        return self.add_to_property_list('uri', uri)

    def uris(self):
        """Return the current list of URIs"""
        return self._get_config_property('uri')

    def set_database(self, dbname):
        """Specify documents database"""
        return self._set('database', dbname)

    def database(self):
        """Get the current documents database"""
        return self._get('database')

    def set_forest(self, forest):
        """Set the forest for document inserts"""
        return self._set('forest-name', forest)

    def forest(self):
        """Get the forest that will be used for document inserts"""
        return self._get('forest')

    def set_categories(self, cats):
        """Set list of categories of data to insert or update"""
        return self.set_property_list('category', cats)

    def set_category(self, cat):
        """Set the single category of data to insert or update"""
        self._config['category'] = []
        if cat is not None:
            self._config['category'].append(cat)
        return self

    def add_category(self, cat):
        """
        Add a category to the list of categories of data to insert or
        update
        """
        return self.add_to_property_list('category', cat)

    def categories(self):
        """Get the list of cateories of data to insert or update"""
        return self._get_config_property('category')

    def set_format(self, form):
        """
        Set the format parameter for document inserts or updates.

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
        """Get the current format."""
        return self._get('format')

    def set_transform(self, transform):
        """Set the name of the transform to apply"""
        return self._set('transform', transform)

    def transform(self):
        """Get the current transform name"""
        return self._get('transform')

    def set_transform_param(self, name, value):
        """
        Set a single transformation parameter. Any existing
        parameters are removed.

        The "trans:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['transparam'] = []
        return self.add_transform_param(name, value)

    def set_transform_params(self, tuples):
        """
        Set a group of transformation parameters. Each name/value pair must
        be provided as a tuple. Any existing parameters are removed.
        Specifying None will remove all parameters.

        The "trans:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['transparam'] = []
        if tuples is not None:
            self.add_transform_params(tuples)
        return self

    def add_transform_param(self, name, value):
        """Add a transformation parameter.

        The "trans:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['transparam'].append("trans:" + name + "=" + value)
        return self

    def add_transform_params(self, tuples):
        """
        Add a group of transformation parameters. Each name/value pair must
        be provided as a tuple.

        The "trans:" prefix required by the API will be provided for you
        automatically.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_transform_param(self, pair[0], pair[1])
        return self

    def transform_param(self, name):
        """Get the value of a single transformation parameter"""
        if 'transparam' in self._config:
            key = "trans:" + name + "="
            for item in self._config['transparam']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def transform_params(self):
        """Get the values of all the transformation parameters.

        The values are returned as a list of tuples
        """
        params = []
        if 'transparam' in self._config:
            for item in self._config['transparam']:
                params.append(tuple(item[6:].split('=')))
            return params
        else:
            return None

    def set_txid(self, txid):
        """Set the transaction id.

        Remember that the transaction in question must have been created in
        the same database as the document inserts or updates.
        """
        return self._set('txid', txid)

    def txid(self):
        """Get the current transaction id."""
        return self._get('txid')

    def set_accept(self, accept):
        """Set the accept header for the requests."""
        return self._set('accept', accept)

    def accept(self):
        """Get the current accept header"""
        return self._get('accept')

    def set_content_type(self, content_type):
        """Set the content type for inserts and updates"""
        return self._set('content-type', content_type)

    def content_type(self):
        """Get the current content type"""
        return self._get('content-type')

    def set_if_none_match(self, version):
        raise UnsupportedOperation("Not implemented yet")

    def set_range(self, start=None, end=None):
        raise UnsupportedOperation("Not implemented yet")

    def set_quality(self, quality):
        """Set the quality value"""
        return self._set('quality', quality)

    def quality(self):
        """Get the current quality value"""
        return self._get('quality')

    def set_permission(self, role, value):
        """
        Set a single permission. Any existing permissions are removed.

        The "perm:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['permission'] = []
        return self.add_permission(role, value)

    def set_permissions(self, tuples):
        """
        Set a group of permissions.

        Each name/value pair must be provided as a tuple. Any existing
        permissions are removed.

        The "perm:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['permission'] = []
        if tuples is not None:
            self.add_permissions(tuples)
        return self

    def add_permission(self, role, value):
        """
        Set a permission to the list of permissions.

        The "perm:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['permission'].append("perm:" + role + "=" + value)
        return self

    def add_permissions(self, tuples):
        """
        Add a group of permissions.

        Each name/value pair must be provided as a tuple.

        The "perm:" prefix required by the API will be provided for you
        automatically.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_permission(self, pair[0], pair[1])
        return self

    def permission(self, role):
        """Get the permissions associated with a single role"""
        if 'permission' in self._config:
            key = "perm:" + role + "="
            for item in self._config['permission']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def permissions(self):
        """Get all the permissions as a list of tuples."""
        perms = []
        if 'permission' in self._config:
            for item in self._config['permission']:
                perms.append(tuple(item[5:].split('=')))
            return perms
        else:
            return None

    def set_property(self, name, value):
        """
        Set a single property. Any existing properties are removed.

        The "prop:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['property'] = []
        return self.add_property(name, value)

    def set_properties(self, tuples):
        """
        Set a group of properties.

        Each name/value pair must be provided as a tuple. Any existing
        permissions are removed.

        The "prop:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['property'] = []
        if tuples is not None:
            self.add_properties(tuples)
        return self

    def add_property(self, name, value):
        """
        Add a single property.

        The "prop:" prefix required by the API will be provided for you
        automatically.
        """
        self._config['property'].append("prop:" + name + "=" + value)
        return self

    def add_properties(self, tuples):
        """
        Add a group of properties.

        Each name/value pair must be provided as a tuple.

        The "prop:" prefix required by the API will be provided for you
        automatically.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_property(pair[0], pair[1])
        return self

    def property(self, name):
        """Get the value of a specific property"""
        if 'property' in self._config:
            key = "prop:" + name + "="
            for item in self._config['property']:
                if item.startswith(key):
                    return item[len(key):]
        return None

    def properties(self):
        """Get all the properties as a list of tuples"""
        props = []
        if 'property' in self._config:
            for item in self._config['property']:
                props.append(tuple(item[5:].split('=')))
            return props
        else:
            return None

    def set_extract(self, value):
        """Set the extract value"""
        return self._set('extract', value)

    def extract(self):
        """Get the extract value"""
        return self._get('extract')

    def set_repair(self, value):
        """Set the repair value"""
        return self._set('repair', value)

    def repair(self):
        """Get the repair value"""
        return self._get('repair')

    def set_lang(self, language):
        """Set the language"""
        return self._set('lang', language)

    def lang(self):
        """Get the language"""
        return self._get('lang')

    def set_temporal_collection(self, collection):
        """Set the temporal collection"""
        return self._set('temporal-collection', collection)

    def temporal_collection(self):
        """Get the temporal collection"""
        return self._get('temporal-collection')

    def set_system_time(self, time):
        """Set the system time associated with a temporal collection"""
        return self._set('system-time', time)

    def system_time(self):
        """Get the system time associated with a temporal collection"""
        return self._get('system-time')

    def clear(self):
        """Clear the documents object. This removes all previous settings
        and returns the object to its initial state."""
        self._config = {}
        self._config['uri'] = []
        self._config['category'] = []
        self._config['transparam'] = []
        self._config['permission'] = []
        self._config['property'] = []
        self._config['accept'] = "application/xml"
        self._config['content-type'] = "application/xml"

    def _plist(self, propname):
        """An internal method that constructs a URI parameter list"""
        param = ""

        if propname in self._config:
            for prop in self._config[propname]:
                param = param + "&" + propname + "=" + prop

        return param

    def get(self, uri=None, connection=None):
        """
        Perform an HTTP GET on the document(s) described by this object.

        If a URI is specified, it will be used irrespective of the URI setting
        in the object. If it isn't specified, the object URI(s) will be used.

        If more than one URI is specified, the response will be a
        multipart/mixed payload.
        """
        if connection is None:
            connection = self.connection

        if uri is None:
            uris = []
            for uri in self._config['uri']:
                uris.append("uri=" + uri)
        else:
            uris = ["uri=" + uri]

        params = "?" + "&".join(uris)

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
        """
        Perform an HTTP PUT on the document described by this object.

        If a URI is specified, it will be used irrespective of the URI setting
        in the object. If it isn't specified, the object must specify a single
        URI.

        The data must be specified. For application/json data, a Python
        dictionary may be specified.
        """
        if connection is None:
            connection = self.connection

        if uri is None:
            if len(self._config['uri']) != 1:
                raise InvalidAPIRequest("Must PUT with exactly one URI")
            uri = self._config['uri'][0]

        params = "?uri=" + uri

        for key in ['database', 'format', 'quality', 'extract', 'repair', \
                        'transform', 'forest-name', 'txid', 'lang', \
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

        response = connection.put(uri + params, payload=data, \
                                      content_type=self._config['content-type'], \
                                      accept=self._config['accept'])
        return response

    def delete(self, uri=None, connection=None):
        """
        Perform an HTTP DELETE on the document(s) described by this object.

        If a URI is specified, it will be used irrespective of the URI setting
        in the object. If it isn't specified, all of the URIs specified in
        the object will be deleted.
        """
        if connection is None:
            connection = self.connection

        if uri is None:
            uris = []
            for uri in self._config['uri']:
                uris.append("uri=" + uri)
        else:
            uris = ["uri=" + uri]

        params = "?" + "&".join(uris)

        for key in ['database', 'txid', 'temporal-collection', 'system-time']:
            if key in self._config:
                params = params + "&" + key + "=" + self._config[key]

        params = params + self._plist("category")

        uri = connection.client_uri("documents")

        response = connection.delete(uri + params)

        return response
