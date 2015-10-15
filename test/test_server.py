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
from marklogic.connection import Connection
from marklogic.models.server import Server, HttpServer, XdbcServer
from marklogic.models.server import OdbcServer, WebDAVServer
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

    def test_ssl_certificate_pems(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        server = HttpServer("foo-http", "Default", 10101, '/', 'Documents')
        self.assertEqual(server.server_name(), "foo-http")
        server.create(connection)
        self.assertIsNotNone(server)
        self.assertEqual("http", server.server_type())

        pem1 = "-----BEGIN CERTIFICATE-----\n\
MIICgjCCAeugAwIBAgIBBDANBgkqhkiG9w0BAQQFADBTMQswCQYDVQQGEwJVUzEc\n\
MBoGA1UEChMTRXF1aWZheCBTZWN1cmUgSW5jLjEmMCQGA1UEAxMdRXF1aWZheCBT\n\
ZWN1cmUgZUJ1c2luZXNzIENBLTEwHhcNOTkwNjIxMDQwMDAwWhcNMjAwNjIxMDQw\n\
MDAwWjBTMQswCQYDVQQGEwJVUzEcMBoGA1UEChMTRXF1aWZheCBTZWN1cmUgSW5j\n\
LjEmMCQGA1UEAxMdRXF1aWZheCBTZWN1cmUgZUJ1c2luZXNzIENBLTEwgZ8wDQYJ\n\
KoZIhvcNAQEBBQADgY0AMIGJAoGBAM4vGbwXt3fek6lfWg0XTzQaDJj0ItlZ1MRo\n\
RvC0NcWFAyDGr0WlIVFFQesWWDYyb+JQYmT5/VGcqiTZ9J2DKocKIdMSODRsjQBu\n\
WqDZQu4aIZX5UkxVWsUPOE9G+m34LjXWHXzr4vCwdYDIqROsvojvOm6rXyo4YgKw\n\
Env+j6YDAgMBAAGjZjBkMBEGCWCGSAGG+EIBAQQEAwIABzAPBgNVHRMBAf8EBTAD\n\
AQH/MB8GA1UdIwQYMBaAFEp4MlIR21kWNl7fwRQ2QGpHfEyhMB0GA1UdDgQWBBRK\n\
eDJSEdtZFjZe38EUNkBqR3xMoTANBgkqhkiG9w0BAQQFAAOBgQB1W6ibAxHm6VZM\n\
zfmpTMANmvPMZWnmJXbMWbfWVMMdzZmsGd20hdXgPfxiIKeES1hl8eL5lSE/9dR+\n\
WB5Hh1Q+WKG1tfgq73HnvMP2sUlG4tega+VWeponmHxGYhTnyfxuAxJ5gDgdSIKN\n\
/Bf+KpYrtWKmpj29f5JZzVoqgrI3eQ==\n\
-----END CERTIFICATE-----"

        pem2 = "-----BEGIN CERTIFICATE-----\n\
MIICkDCCAfmgAwIBAgIBATANBgkqhkiG9w0BAQQFADBaMQswCQYDVQQGEwJVUzEc\n\
MBoGA1UEChMTRXF1aWZheCBTZWN1cmUgSW5jLjEtMCsGA1UEAxMkRXF1aWZheCBT\n\
ZWN1cmUgR2xvYmFsIGVCdXNpbmVzcyBDQS0xMB4XDTk5MDYyMTA0MDAwMFoXDTIw\n\
MDYyMTA0MDAwMFowWjELMAkGA1UEBhMCVVMxHDAaBgNVBAoTE0VxdWlmYXggU2Vj\n\
dXJlIEluYy4xLTArBgNVBAMTJEVxdWlmYXggU2VjdXJlIEdsb2JhbCBlQnVzaW5l\n\
c3MgQ0EtMTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAuucXkAJlsTRVPEnC\n\
UdXfp9E3j9HngXNBUmCbnaEXJnitx7HoJpQytd4zjTov2/KaelpzmKNc6fuKcxtc\n\
58O/gGzNqfTWK8D3+ZmqY6KxRwIP1ORROhI8bIpaVIRw28HFkM9yRcuoWcDNM50/\n\
o5brhTMhHD4ePmBudpxnhcXIw2ECAwEAAaNmMGQwEQYJYIZIAYb4QgEBBAQDAgAH\n\
MA8GA1UdEwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAUvqigdHJQa0S3ySPY+6j/s1dr\n\
aGwwHQYDVR0OBBYEFL6ooHRyUGtEt8kj2Puo/7NXa2hsMA0GCSqGSIb3DQEBBAUA\n\
A4GBADDiAVGqx+pf2rnQZQ8w1j7aDRRJbpGTJxQx78T3LUX47Me/okENI7SS+RkA\n\
Z70Br83gcfxaz2TE4JaY0KNA4gGK7ycH8WUBikQtBmV1UsCGECAhX2xrD2yuCRyv\n\
8qIYNMR1pHMc8Y3c7635s3a0kr/clRAevsvIO1qEYBlWlKlV\n\
-----END CERTIFICATE-----"

        server.add_ssl_client_certificate_pem(pem1)
        server.update(connection)
        server.read(connection)

        self.assertEqual(1, len(server.ssl_client_certificate_pems()))

        server.set_ssl_client_certificate_pems([pem1,pem2])
        server.update(connection)
        server.read(connection)

        self.assertEqual(2, len(server.ssl_client_certificate_pems()))

        server.delete(connection)
        server = Server.lookup(connection, "foo-http")
        self.assertIsNone(server)

if __name__ == "__main__":
    unittest.main()
