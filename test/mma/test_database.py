# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

#
# Copyright 2015 MarkLogic Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
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
# Norman Walsh      10/12/2015     Initial development
#

import unittest
from marklogic import MarkLogic
from marklogic.mma import MMA
from marklogic.connection import Connection
from requests.auth import HTTPDigestAuth
from test.resources import TestConnection as tc

class MmaTestDatabase(unittest.TestCase):
    """
    Basic creation test function.
    """
    def __init__(self, argv):
        super().__init__(argv)
        self.connection = Connection(tc.hostname,
                                     HTTPDigestAuth(tc.admin, tc.password))
        self.marklogic = MarkLogic(self.connection)

    def test_create_database(self):
        dbname = 'test-mma-database'

        mma = MMA(self.connection)
        mma.run(['create','database',dbname])

        self.assertTrue(dbname in self.marklogic.databases())

        mma.run(['delete','database',dbname])

        self.assertFalse(dbname in self.marklogic.databases())


if __name__ == "__main__":
    unittest.main()
