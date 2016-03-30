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

import logging
from urllib import parse
from marklogic.utilities import PropertyLists
from marklogic.client.exceptions import InvalidAPIRequest, UnsupportedOperation
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

class Documents(PropertyLists):
    """
    The Documents class encapsulates a call to the Client API v1/documents
    endpoint.
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create a Documents object.
        """
        self._config = {}
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.documents")

        self._content = None
        self._metadata = None
        self._metadata_content_type = None
        self.permissions = []
        self.properties = []
        self.transparams = []

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
        return self._get('uri')

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
        return self._get('category')

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
        """
        self.transparams = []
        return self.add_transform_param(name, value)

    def set_transform_params(self, tuples):
        """
        Set a group of transformation parameters. Each name/value pair must
        be provided as a tuple. Any existing parameters are removed.
        Specifying None will remove all parameters.
        """
        self.transparams = []
        if tuples is not None:
            self.add_transform_params(tuples)
        return self

    def add_transform_param(self, name, value):
        """Add a transformation parameter.
        """
        self.transparams = []
        self.transparams.append((name, value))
        return self

    def add_transform_params(self, tuples):
        """
        Add a group of transformation parameters. Each name/value pair must
        be provided as a tuple.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.transparams.append(pair)
        return self

    def transform_param(self, name):
        """Get the value(s) of a single transformation parameter"""
        values = []
        for pair in self.transparams:
            if pair[0] == name:
                values.append(pair[1])
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values

    def transform_params(self):
        """Get the values of all the transformation parameters.

        The values are returned as a list of tuples
        """
        if self.transparams:
            return self.transparams
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
        return self._set('quality', str(quality))

    def quality(self):
        """Get the current quality value"""
        return self._get('quality')

    def set_collection(self, value):
        """
        Set a single collection. Any existing collections are removed.
        """
        self._config['collection'] = []
        if value is not None:
            self.add_collection(value)
        return self

    def set_collections(self, values):
        """
        Set a list of collections.
        """
        self._config['collection'] = []
        return self.add_collections(values)

    def add_collection(self, value):
        """
        Add a collection to the list of collections.
        """
        self._config['collection'].append(value)
        return self

    def add_collections(self, values):
        """
        Add a list of collections.
        """
        for value in values:
            self.add_collection(value)
        return self

    def collections(self):
        """Get all the collections"""
        return self._config['collection']

    def set_permission(self, role, value):
        """
        Set a single permission. Any existing permissions are removed.
        """
        self.permissions = []
        return self.add_permission(role, value)

    def set_permissions(self, tuples):
        """
        Set a group of permissions.

        Each name/value pair must be provided as a tuple. Any existing
        permissions are removed.
        """
        self.permissions = []
        if tuples is not None:
            self.add_permissions(tuples)
        return self

    def add_permission(self, role, value):
        """
        Set a permission to the list of permissions.
        """
        self.permissions.append((role,value))
        return self

    def add_permissions(self, tuples):
        """
        Add a group of permissions.

        Each name/value pair must be provided as a tuple.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.permissions.append(pair)
        return self

    def permission(self, role):
        """Get the permissions associated with a single role"""
        values = []
        for pair in self.permissions:
            if pair[0] == role:
                values.append(pair[1])
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values

    def permissions(self):
        """Get all the permissions as a list of tuples."""
        if self.permissions:
            return self.permissions
        else:
            return None

    def set_property(self, name, value):
        """
        Set a single property. Any existing properties are removed.
        The value must be a string. To set complex properties, you
        must build the payload yourself and call set_metadata()
        """
        self.properties = []
        return self.add_property(name, value)

    def set_properties(self, tuples):
        """
        Set a group of properties.

        Each name/value pair must be provided as a tuple. Any existing
        permissions are removed.
        """
        self.properties = []
        if tuples is not None:
            self.add_properties(tuples)
        return self

    def add_property(self, name, value):
        """
        Add a single property.
        """
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            self.properties.append((name, value))
        else:
            raise InvalidAPIRequest("Property value is not a string")
        return self

    def add_properties(self, tuples):
        """
        Add a group of properties.

        Each name/value pair must be provided as a tuple.
        """
        for pair in tuples:
            if type(pair) is not tuple or len(pair) != 2:
                raise InvalidAPIRequest("Not a tuple")
            self.add_property(pair[0], pair[1])
        return self

    def property(self, name):
        """Get the value(s) of a specific property"""
        values = []
        for pair in self.properties:
            if pair[0] == name:
                values.append(pair[1])
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values

    def properties(self):
        """Get all the properties as a list of tuples"""
        if self.properties:
            return self.properties
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

    def set_metadata(self, metadata, meta_content_type):
        """Set arbitrary metadata.

        You must format it in XML or JSON according to the rules of the
        Client API. If you set arbitrary metadata, you cannot call any
        other methods that set metadata properties. You also cannot
        specify the forest.
        """
        self._metadata = metadata
        if meta_content_type in ["application/json", "application/xml"]:
            self._metadata_content_type = meta_content_type
        else:
            raise InvalidAPIRequest("Metadata format must be 'application/json' or 'application/xml'")

    def metadata_content_type(self):
        """Return the content type of arbitrary metadata.
        Return None if arbitrary metadata has not been assigned.
        """
        if self._metadata_content_type is None:
            return "application/xml"
        else:
            return self._metadata_content_type

    def metadata(self):
        """Returns the metadata.

        If arbitrary metadata was assigned, it is returned and the format
        parameter is ignored. If not, then metadata is returned as
        an XML string.
        """
        if self._metadata:
            return self._metadata

        xml = '<rapi:metadata xmlns:rapi="http://marklogic.com/rest-api" ' \
          + 'xmlns:prop="http://marklogic.com/xdmp/property">\n'

        if 'quality' in self._config:
            xml += "<rapi:quality>{}</rapi:quality>\n".format(self._config['quality'])

        if self._config['collection']:
            xml += "<rapi:collections>\n"
            for collection in self._config['collection']:
                xml += "<rapi:collection>{}</rapi:collection>\n".format(collection)
            xml += "</rapi:collections>\n"

        if self.permissions:
            xml += "<rapi:permissions>\n"
            for pair in self.permissions:
                xml += "<rapi:permission>\n"
                xml += "  <rapi:role-name>{}</rapi:role-name>".format(pair[0])
                xml += "  <rapi:capability>{}</rapi:capability>".format(pair[1])
                xml += "</rapi:permission>\n"
            xml += "</rapi:permissions>\n"

        if self.properties:
            xml += "<prop:properties>\n"
            for pair in self.properties:
                xml += "<{}>{}</{}>\n".format(pair[0], pair[1], pair[0])
            xml += "</rapi:properties>\n"

        xml += "</rapi:metadata>"
        return xml

    def set_content(self, data, content_type=None):
        """Set content.

        For single documents, you can simply pass the data to the put method.
        However, if you want to use the BulkLoader, you must set the content
        before adding it to the bulk loader.
        """
        self._content = data
        if content_type is not None:
            self.set_content_type(content_type)
        return self

    def content(self):
        """Return the content, if any"""
        return self._content

    def clear(self):
        """Clear the documents object. This removes all previous settings
        and returns the object to its initial state."""
        self._config = {}
        self._config['uri'] = []
        self._config['category'] = []
        self._config['collection'] = []
        self._config['accept'] = "application/xml"
        self._config['content-type'] = "application/xml"
        self._content = None
        self._metadata = None
        self._metadata_content_type = None
        self.permissions = []
        self.properties = []
        self.transparams = []

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

        params = []
        if uri is None:
            for uri in self._config['uri']:
                params.append("uri=" + parse.quote(uri))
        else:
            params.append("uri=" + parse.quote(uri))

        for key in ['database', 'format', 'transform', 'txid']:
            if key in self._config:
                params.append("{}={}".format(key, self._config[key]))

        for value in self._config['category']:
            params.append("category={}".format(value))

        for pair in self.transparams:
            params.append("trans:{}={}".format(pair[0], pair[1]))

        uri = connection.client_uri("documents")

        uri = uri + "?" + "&".join(params)

        response = connection.get(uri, accept=self._config['accept'])
        return response

    def put(self, data=None, uri=None, connection=None):
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

        if data is None:
            if self._content is None:
                raise InvalidAPIRequest("Attempt to upload doc with no content")
            data = self._content

        if uri is None:
            if len(self._config['uri']) != 1:
                raise InvalidAPIRequest("Must PUT with exactly one URI")
            uri = self._config['uri'][0]

        # You must not mix individual metadata properties with arbitrary metadata
        if self._metadata is not None:
            for key in self._config:
                if key == 'category' or key == 'collection':
                    if self._config[key]:
                        raise InvalidAPIRequest("Cannot mix individual and bulk metadata1")
                elif key == 'uri':
                    if self._config[key] and len(self._config[key]) != 1:
                        raise InvalidAPIRequest("Cannot mix individual and bulk metadata4")
                elif (key == 'accept' or key == 'content-type' or key == 'database' \
                          or key == 'transform' or key == 'txid' \
                          or key == 'temporal-collection' or key == 'system-time'):
                    pass
                else:
                    raise InvalidAPIRequest("Cannot mix individual and bulk metadata2")
            if self.permissions or self.properties:
                raise InvalidAPIRequest("Cannot mix individual and bulk metadata3")
            return self._put_mixed(data, uri, connection)
        else:
            return self._put_uriparams(data, uri, connection)

    def _put_uriparams(self, data, uri, connection):
        """
        Put the document directly using URI parameters.
        """

        params = ["uri=" + uri]
        for key in ['database', 'format', 'quality', 'extract', 'repair', \
                        'transform', 'forest-name', 'txid', 'lang', \
                        'temporal-collection', 'system-time']:
            if key in self._config:
                params.append("{}={}".format(key, self._config[key]))

        for value in self._config['category']:
            params.append("category={}".format(value))
        for value in self._config['collection']:
            params.append("collection={}".format(value))

        for pair in self.permissions:
            params.append("perm:{}={}".format(pair[0], pair[1]))

        for pair in self.properties:
            params.append("prop:{}={}".format(pair[0], pair[1]))

        for pair in self.transparams:
            params.append("trans:{}={}".format(pair[0], pair[1]))

        uri = connection.client_uri("documents")

        uri = uri + "?" + "&".join(params)

        response = connection.put(uri, payload=data, \
                                      content_type=self._config['content-type'], \
                                      accept=self._config['accept'])
        return response

    def _put_mixed(self, data, target, connection):
        """
        Put the document using the bulk interface (because it has
        arbitrary metadata).
        """

        params = []
        for key in ['database', 'transform', 'txid', \
                        'temporal-collection', 'system-time']:
            if key in self._config:
                params.append("{}={}".format(key, self._config[key]))

        for pair in self.transparams:
            params.append("trans:{}={}".format(pair[0], pair[1]))

        meta = self.metadata()
        if self.metadata_content_type() is None:
            metact = "application/xml"
        else:
            metact = self.metadata_content_type()

        uri = connection.client_uri("documents")
        if params:
            uri = uri + "?" + "&".join(params)

        datact = self._config['content-type']

        fields = []
        rf = RequestField(name="meta1", data=meta, filename=target)
        rf.make_multipart(content_disposition='attachment; category=metadata', \
                              content_type=metact)
        fields.append(rf)

        rf = RequestField(name="data1", data=data, filename=target)
        rf.make_multipart(content_disposition='attachment', \
                              content_type=datact)
        fields.append(rf)

        post_body, content_type = encode_multipart_formdata(fields)

        post_ct = ''.join(('multipart/mixed',) \
                              + content_type.partition(';')[1:])

        response = connection.post(uri, payload=post_body, content_type=post_ct)

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

        params = []
        if uri is None:
            for uri in self._config['uri']:
                params.append("uri=" + uri)
        else:
            params.append("uri=" + uri)

        for key in ['database', 'txid', 'temporal-collection', 'system-time']:
            if key in self._config:
                params.append("{}={}".format(key, self._config[key]))

        for value in self._config['category']:
            params.append("category={}".format(value))

        uri = connection.client_uri("documents")

        uri = uri + "?" + "&".join(params)

        response = connection.delete(uri)

        return response
