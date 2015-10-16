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
from marklogic.models.certificate.request import Request

class TestCertRequest(unittest.TestCase):
    def test_request(self):
        req = Request(countryName="US", stateOrProvinceName="TX",
                      localityName="Austin", organizationName="MarkLogic",
                      emailAddress="Norman.Walsh@marklogic.com",
                      version=0)

        self.assertEqual("US", req.countryName())
        self.assertEqual("TX", req.stateOrProvinceName())
        self.assertEqual("Austin", req.localityName())
        self.assertEqual("Norman.Walsh@marklogic.com", req.emailAddress())
        self.assertEqual(0, req.version())
        self.assertIsNone(req.v3ext())

        ext = {
            "nsCertType": {
                "critical": False,
                "value": "SSL Server"
                },
            "subjectKeyIdentifier": {
                "critical": False,
                "value": "B2:2C:0C:F8:5E:A7:44:B7"
                }
            }

        req = Request(countryName="US", stateOrProvinceName="TX",
                      localityName="Austin", organizationName="MarkLogic",
                      emailAddress="Norman.Walsh@marklogic.com",
                      version=0, v3ext=ext)

        self.assertEqual("SSL Server", req.v3ext()["nsCertType"]["value"])


if __name__ == "__main__":
    unittest.main()
