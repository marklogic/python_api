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
# Philip Barber      02/14/2016     Initial development
#

import unittest
from requests.auth import HTTPDigestAuth
from marklogic.models import Database, Server, Forest
from marklogic.connection import Connection
from test.ssl.resources import TestConnection as tc

class TestSslConnection(unittest.TestCase):
    """
    Basic creation test function.
    """
    def test_check_ssl_manage_server(self):
        conn = Connection(tc.hostname,
             HTTPDigestAuth(tc.admin, tc.password),
             protocol="https",
             verify = "",
             management_port=tc.sslport)
        server = Server.lookup(conn, "Default|Manage")
        self.assertIsNotNone(server)
        self.assertEqual('Manage', server.server_name())

if __name__ == "__main__":
    unittest.main()
