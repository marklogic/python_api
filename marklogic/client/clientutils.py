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
import json, logging, time
from marklogic.connection import Connection
from marklogic.client.exceptions import *
from marklogic.client.eval import Eval
from requests_toolbelt import MultipartDecoder

class ClientUtils:
    """
    The ClientUtils class encapsulates an object with a variety of utility methods.
    They're not static because it's convenient to have the connection cached.
    """
    def __init__(self,connection=None,save_connection=True):
        """
        Create a ClientUtils object.
        """
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.client.utils")

    def uris(self, database, connection=None):
        """
        Get a list of all the URIs in a database.
        """

        uris = []

        if connection is None:
            connection = self.connection

        mleval = Eval(connection)
        mleval.set_xquery("xquery version '1.0-ml'; cts:uris()")
        mleval.set_database(database)
        response = mleval.eval()

        if 'content-type' in response.headers:
            if response.headers['content-type'].startswith("multipart/mixed"):
                decoder = MultipartDecoder.from_response(response)
                for part in decoder.parts:
                    uris.append(part.text)

        return uris
