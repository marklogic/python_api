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
# Norman Walsh      05/13/2015     Initial development

from __future__ import unicode_literals, print_function, absolute_import

import unittest
from marklogic.connection import Connection
from marklogic.models.certificate.authority import Authority
from test.resources import TestConnection as tc

class TestCertAuthority(unittest.TestCase):
    def test_list(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        names = Authority.list(connection, include_names=True)

        self.assertGreater(len(names), 100)
        found = False
        for name in names:
            found = found or "Equifax" in name
        self.assertEqual(True, found)

    def test_create(self):
        pem = ("-----BEGIN CERTIFICATE-----\n"
               "MIIC3TCCAkYCCQCJtpKDQbobyTANBgkqhkiG9w0BAQsFADCBsjELMAkGA1UEBhMC\n"
               "VVMxCzAJBgNVBAgMAlRYMQ8wDQYDVQQHDAZBdXN0aW4xHjAcBgNVBAoMFU1hcmtM\n"
               "b2dpYyBDb3Jwb3JhdGlvbjEXMBUGA1UECwwOVFggRW5naW5lZXJpbmcxITAfBgNV\n"
               "BAMMGE1hcmtMb2dpYyBUWCBFbmdpbmVlcmluZzEpMCcGCSqGSIb3DQEJARYabm9y\n"
               "bWFuLndhbHNoQG1hcmtsb2dpYy5jb20wHhcNMTQwODI3MTkyMzQyWhcNMTUwODI3\n"
               "MTkyMzQyWjCBsjELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAlRYMQ8wDQYDVQQHDAZB\n"
               "dXN0aW4xHjAcBgNVBAoMFU1hcmtMb2dpYyBDb3Jwb3JhdGlvbjEXMBUGA1UECwwO\n"
               "VFggRW5naW5lZXJpbmcxITAfBgNVBAMMGE1hcmtMb2dpYyBUWCBFbmdpbmVlcmlu\n"
               "ZzEpMCcGCSqGSIb3DQEJARYabm9ybWFuLndhbHNoQG1hcmtsb2dpYy5jb20wgZ8w\n"
               "DQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAJSo3wFMDvTV7Q+4NDDMu9aJZ6uK4l8b\n"
               "ACIk5/Ug+MoST+CuIfeBlb2Y6dxNCwkADwVPpykslDcHYFygxFIcnHHVhgqZ0xzu\n"
               "LPXBagXmHyj+mb6im1tkbqAxQ7gj/SDeCnQYRIwNRlGgWZJFViaYJH3CC8G/f16F\n"
               "IhDyQS3h28W3AgMBAAEwDQYJKoZIhvcNAQELBQADgYEAWbidV4huPlf8Ac0c3Cbs\n"
               "Nx2xogODSjNPKqwug0Y3jKx33uxeY7i9oParWSnVFkG0JYUZEfrO5fmtS6JSA1Lk\n"
               "e3BioC9xgclEYFiDoZSARasL8hdNvu7v+EYZEnS43rR4M7CQiq/Tf50o4VjiVM9S\n"
               "I0Bo+VZSaShQKipBEHS8sP8=\n"
               "-----END CERTIFICATE-----\n")

        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        cert = Authority.create(connection, pem)

        self.assertIsNotNone(cert)
        self.assertEqual('true', cert.enabled())
        self.assertIsNotNone(cert.properties())

        cert.delete(connection)


    def test_lookup(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        names = Authority.list(connection)
        auth = Authority.lookup(connection, names[0])

        self.assertIsNotNone(auth)
        self.assertEqual(auth.certificate_id(), names[0])

# Not yet supported by underlying API
#    def test_toggle_enable(self):
#        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
#
#        names = Authority.list(connection)
#        auth = Authority.lookup(connection, names[0])
#
#        newvalue = not auth.enabled()
#        auth.set_enabled(newvalue)
#        auth.update(connection)
#
#        newauth = Authority.lookup(connection, names[0])
#        self.assertIsNotNone(newauth)
#        self.assertEqual(newvalue, newauth.enabled())
#
#        auth.set_enabled(not newvalue)
#        auth.update(connection)
#        auth.read(connection)
#
#        self.assertEqual(not newvalue, auth.enabled())

if __name__ == "__main__":
    unittest.main()
