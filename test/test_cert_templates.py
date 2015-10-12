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
from marklogic.models.certificate.request import Request
from marklogic.models.certificate.template import Template
from test.resources import TestConnection as tc

class TestRequest(unittest.TestCase):
    def test_template(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        req = Request(countryName="US", stateOrProvinceName="TX",
                      localityName="Austin", organizationName="MarkLogic",
                      emailAddress="Norman.Walsh@marklogic.com",
                      version=0)
        temp = Template("Test Template", "Test description", req)

        self.assertEqual("Test Template", temp.template_name())

        temp.create(connection)

        names = Template.list(connection)

        self.assertGreater(len(names), 0)
        self.assertIn(temp.template_id(), names)

        temp.set_template_name("New Name")
        temp.set_template_description("New Description")
        temp.update(connection)
        self.assertIsNotNone(temp)

        newtemp = Template.lookup(connection, temp.template_id())
        self.assertEqual(temp.template_name(), newtemp.template_name())

        temp.delete(connection)

        self.assertIsNotNone(temp)

if __name__ == "__main__":
    unittest.main()
