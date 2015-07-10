# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

#
# Copyright 2015 MarkLogic Corporation
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
# Norman Walsh      05/01/2015     Initial development
#

import unittest
from marklogic.models import Connection, Server, HttpServer, XdbcServer, OdbcServer, WebDAVServer
from test.resources import TestConnection as tc

class TestServer(unittest.TestCase):

    def test_list(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        names = Server.list(connection)
        self.assertGreater(len(names), 3)
        self.assertIn("Default|Manage", names)

    def test_lookup(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        server = Server.lookup(connection, "Manage")

        self.assertIsNotNone(server)
        self.assertEqual(server.server_name(), "Manage")

    def test_load(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        server = HttpServer("Manage", "Default")
        self.assertEqual(server.server_name(), "Manage")
        self.assertIsNotNone(server.read(connection))
        self.assertEqual("http", server.server_type())

    def test_create_http_server(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        server = HttpServer("foo-http", "Default", 10101, '/', 'Documents')
        self.assertEqual(server.server_name(), "foo-http")
        server.create(connection)
        self.assertIsNotNone(server)
        self.assertEqual("http", server.server_type())
        server.delete(connection)
        server = Server.lookup(connection, "foo-http")
        self.assertIsNone(server)

    def test_create_odbc_server(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        server = OdbcServer("foo-odbc", "Default", 10101, '/', 'Documents')
        self.assertEqual(server.server_name(), "foo-odbc")
        server.create(connection)
        self.assertIsNotNone(server)
        self.assertEqual("odbc", server.server_type())
        server.delete(connection)
        server = Server.lookup(connection, "foo-odbc")
        self.assertIsNone(server)

    def test_create_xdbc_server(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        server = XdbcServer("foo-xdbc", "Default", 10101, '/', 'Documents')
        self.assertEqual(server.server_name(), "foo-xdbc")
        server.create(connection)
        self.assertIsNotNone(server)
        self.assertEqual("xdbc", server.server_type())
        server.delete(connection)
        server = Server.lookup(connection, "foo-xdbc")
        self.assertIsNone(server)

    def test_create_webdav_server(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        server = WebDAVServer("foo-webdav", "Default", 10101, '/', 'Documents')
        self.assertEqual(server.server_name(), "foo-webdav")
        server.create(connection)
        self.assertIsNotNone(server)
        self.assertEqual("webdav", server.server_type())
        server.delete(connection)
        server = Server.lookup(connection, "foo-webdav")
        self.assertIsNone(server)

if __name__ == "__main__":
    unittest.main()
