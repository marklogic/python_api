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
# Norman Walsh      02/18/2016     Initial development
#

"""
Support the v1/documents bulk loader
"""

from __future__ import unicode_literals, print_function, absolute_import
import logging
from marklogic.utilities import PropertyLists
from marklogic.client.exceptions import InvalidAPIRequest
from marklogic.client.documents import Documents
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

class BulkLoader(PropertyLists):
    """
    The Documents class encapsulates a collection of documents to
    be uploaded in a batch.
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create a BulkLoader object.
        """
        self._config = {}
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.documents.bulkloader")
        self.field_count = 0
        self.fields = []
        self.transparams = []

        self.clear()

    def add(self, document):
        """Add a document to the list of bulk uploads"""
        if not isinstance(document, Documents):
            raise InvalidAPIRequest("You can only pass documents to bulkloader")

        if document.content() is None:
            raise InvalidAPIRequest("You must specify the document content")

        target = document.uris()
        if len(target) != 1:
            raise InvalidAPIRequest("You must specify a single URI")
        else:
            target = target[0]

        self.field_count += 1
        metaname = "meta{}".format(self.field_count)
        dataname = "data{}".format(self.field_count)

        self.logger.debug("Bulk[{}] = {}".format(self.field_count, target))

        rf = RequestField(name=metaname, data=document.metadata(), filename=target)
        rf.make_multipart(content_disposition='attachment; category=metadata', \
                              content_type=document.metadata_content_type())
        self.fields.append(rf)

        rf = RequestField(name=dataname, data=document.content(), filename=target)
        rf.make_multipart(content_disposition='attachment', \
                              content_type=document.content_type())
        self.fields.append(rf)

    def size(self):
        return self.field_count

    def post(self, connection=None):
        if connection is None:
            connection = self.connection

        params = []
        for key in ['database', 'transform', 'txid', \
                        'temporal-collection', 'system-time']:
            if key in self._config:
                params.append("{}={}".format(key, self._config[key]))
        for pair in self.transparams:
            params.append("trans:{}={}".format(pair[0], pair[1]))

        uri = connection.client_uri("documents")
        if params:
            uri = uri + "?" + "&".join(params)

        self.logger.debug("Bulk POST {}: {}".format(self.field_count, uri))

        post_body, content_type = encode_multipart_formdata(self.fields)

        post_ct = ''.join(('multipart/mixed',) \
                              + content_type.partition(';')[1:])

        response = connection.post(uri, payload=post_body, content_type=post_ct)
        self.clear_content()
        return response

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

    def set_database(self, dbname):
        """Specify documents database"""
        return self._set('database', dbname)

    def database(self):
        """Get the current documents database"""
        return self._get('database')

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
        self.field_count = 0
        self.fields = []
        self.transparams = []

    def clear_content(self):
        """Clear the documents object. This removes all previous settings
        and returns the object to its initial state."""
        self.fields = []
        self.field_count = 0

