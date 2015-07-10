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
# Paul Hoehne       03/26/2015     Initial development
#

import unittest
from marklogic.models import Connection, Host
from requests.auth import HTTPDigestAuth
from test.resources import TestConnection as tc


class TestHost(unittest.TestCase):

    def test_list_hosts(self):
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))

        hosts = Host.list(conn)
        self.assertGreater(len(hosts), 0)
        self.assertIsNotNone(hosts[0])

if __name__ == "__main__":
    unittest.main()
