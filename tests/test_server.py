# -*- coding: utf-8 -*-
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

from mlconfig import MLConfig
from marklogic.models.server import Server, HttpServer, XdbcServer
from marklogic.models.server import OdbcServer, WebDAVServer
from marklogic.models.cluster import LocalCluster

class TestServer(MLConfig):

    def test_list(self):
        names = Server.list(self.connection)
        assert len(names) > 3
        assert "Default|Manage" in names

    def test_lookup(self):
        server = Server.lookup(self.connection, "Manage")

        assert server is not None
        assert "Manage" == server.server_name()

    def test_load(self):
        server = HttpServer("Manage", "Default")
        assert "Manage" == server.server_name()
        assert server.read(self.connection) is not None
        assert "http" == server.server_type()

    def test_create_http_server(self):
        server = HttpServer("foo-http", "Default", 10101, '/', 'Documents')
        assert "foo-http" == server.server_name()
        server.create(self.connection)
        assert server is not None
        assert "http" == server.server_type()
        server.delete(self.connection)
        server = Server.lookup(self.connection, "foo-http")
        assert server is None

    def test_create_odbc_server(self):
        server = OdbcServer("foo-odbc", "Default", 10101, '/', 'Documents')
        assert "foo-odbc" == server.server_name()
        server.create(self.connection)
        assert server is not None
        assert "odbc" == server.server_type()
        server.delete(self.connection)
        server = Server.lookup(self.connection, "foo-odbc")
        assert server is None

    def test_create_xdbc_server(self):
        server = XdbcServer("foo-xdbc", "Default", 10101, '/', 'Documents')
        assert "foo-xdbc" == server.server_name()
        server.create(self.connection)
        assert server is not None
        assert "xdbc" == server.server_type()
        server.delete(self.connection)
        server = Server.lookup(self.connection, "foo-xdbc")
        assert server is None

    def test_create_webdav_server(self):
        server = WebDAVServer("foo-webdav", "Default", 10101, '/', 'Documents')
        assert "foo-webdav" == server.server_name()
        server.create(self.connection)
        assert server is not None
        assert "webdav" == server.server_type()
        server.delete(self.connection)
        server = Server.lookup(self.connection, "foo-webdav")
        assert server is None

    def test_ssl_certificate_pems(self):
        cluster = LocalCluster(connection=self.connection)
        version = cluster.version()

        if (version.startswith("4") or version.startswith("5")
            or version.startswith("6") or version.startswith("7")
            or version.startswith("8.0-1") or version.startswith("8.0-2")
            or version.startswith("8.0-3") or version.startswith("8.0-4")):
            pass
        else:
            self._test_ssl_certificate_pems()

    def _test_ssl_certificate_pems(self):
        server = HttpServer("foo-http", "Default", 10101, '/', 'Documents')
        assert "foo-http" == server.server_name()
        server.create(self.connection)
        assert server is not None
        assert "http" == server.server_type()

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
        server.update(self.connection)
        server.read(self.connection)

        assert 1 == len(server.ssl_client_certificate_pems())

        server.set_ssl_client_certificate_pems([pem1,pem2])
        server.update(self.connection)
        server.read(self.connection)

        assert 2 == len(server.ssl_client_certificate_pems())

        server.delete(self.connection)
        server = Server.lookup(self.connection, "foo-http")
        assert server is None
