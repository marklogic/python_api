# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

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
# Philip Barber      02/15/2016     Initial development
#

import unittest
from requests.auth import HTTPDigestAuth
from marklogic.models import Database, Server, Forest
from marklogic.connection import Connection
from test.ssl.resources import TestConnection as tc

class TestPutFile(unittest.TestCase):
    """
    Basic put-file test function.
    """
    def test_put_file(self):
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        
        response = conn.get("http://192.168.200.162:8004/LATEST/config/transforms/simpleExtension")
        self.assertIn("\"status\":\"Not Found\"", response.text)

        data = open("./test/data/simpleExtension.sjs", 'rb').read()
        response = conn.putFile(uri="http://192.168.200.162:8004/LATEST/config/transforms/simpleExtension", data=data, content_type="application/vnd.marklogic-javascript")
        self.assertEqual(204, response.status_code, "PUTting the file should result in a 204 response code")
        
        response = conn.get("http://192.168.200.162:8004/LATEST/config/transforms/simpleExtension")
        self.assertIn("function metadataFilter", response.text)

        response = conn.delete("http://192.168.200.162:8004/LATEST/config/transforms/simpleExtension")
        self.assertEqual(204, response.status_code, "DELETing the file should result in a 204 response code")

if __name__ == "__main__":
    unittest.main()
