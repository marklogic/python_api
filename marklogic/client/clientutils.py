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
Client utility functions
"""

from __future__ import unicode_literals, print_function, absolute_import
import logging
import json
from marklogic.client.eval import Eval
from requests_toolbelt import MultipartDecoder

class ClientUtils:
    """
    The ClientUtils class provides a few utility methods.

    They're not static because it's convenient to have the connection
    cached.
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create a ClientUtils object.
        """
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.utils")

    def uris(self, database, root=None, connection=None):
        """Get a list of all the URIs in a database.

        If root is provided, only URIs that start-with() that string
        will be returned.
        """
        uris = []

        if connection is None:
            connection = self.connection

        mleval = Eval(connection)

        version = "xquery version '1.0-ml';"

        if root is None or root == "":
            mleval.set_xquery("{} cts:uris()".format(version))
        else:
            root = root.replace("'", "&apos;")
            mleval.set_xquery("{} cts:uris()[starts-with(.,'{}')]" \
                                  .format(version, root))

        mleval.set_database(database)
        response = mleval.eval()

        if 'content-type' in response.headers:
            if response.headers['content-type'].startswith("multipart/mixed"):
                decoder = MultipartDecoder.from_response(response)
                for part in decoder.parts:
                    uris.append(part.text)

        return uris

    def last_modified(self, database, uris=None, connection=None):
        """Get a list of last-modified times.

        If uris are provided, returns last modified times for those URIs,
        otherwise attempts to find times for all URIs in the database.
        This requires the database setting to manage last modified times,
        naturally.
        """
        if connection is None:
            connection = self.connection

        mleval = Eval(connection)

        if uris is None:
            leturis = "let $uris := cts:uris()"
        else:
            leturis = "let $uris := cts:uris()["
            comma = ""
            for uri in uris:
                leturis += "{}'{}'".format(comma, uri)
                comma = ", "
            leturis += "]"

        lines = (leturis, \
                     'let $dts  := for $uri in $uris', \
                     '             let $dt := xdmp:document-get-properties($uri, xs:QName("prop:last-modified"))', \
                     '             where $dt', \
                     '             return', \
                     '                object-node { "uri": $uri, "dt": string($dt) }', \
                     'return', \
                     '  array-node { $dts }')

        xquery = "\n".join(lines)
        #print(xquery)
        mleval.set_xquery(xquery)
        mleval.set_database(database)
        response = mleval.eval()

        data = None
        if 'content-type' in response.headers:
            if response.headers['content-type'].startswith("multipart/mixed"):
                decoder = MultipartDecoder.from_response(response)
                for part in decoder.parts:
                    if data is None:
                        data = json.loads(part.text)
                    else:
                        raise RuntimeError("Multipart reply to timestamp query!?")

        return data
