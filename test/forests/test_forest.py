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
# Paul Hoehne       03/28/2015     Initial development
#

import unittest
from marklogic.models import Forest, Host, Connection
from test.resources import TestConnection as tc
from requests.auth import HTTPDigestAuth
from marklogic.models.utilities.validators import ValidationError
from test.settings import DatabaseSettings as ds

class TestForest(unittest.TestCase):
    def test_forest_defaults(self):
        pass

    def test_getters_and_setters(self):
        forest = Forest("Foo", host="bar")
        forest.set_data_directory(ds.data_directory)
        forest.set_large_data_directory(ds.large_data_directory)
        forest.set_fast_data_directory(ds.fast_data_directory)

        self.assertEqual(forest.forest_name(), "Foo")

        forest.set_availability("offline")
        self.assertEqual("offline", forest.availability())

        with self.assertRaises(ValidationError):
            forest.set_availability("foo")

        self.assertEqual("bar", forest.host())

        self.assertEqual(ds.data_directory, forest.data_directory())

        self.assertEqual(ds.fast_data_directory, forest.fast_data_directory())

        self.assertEqual(ds.large_data_directory, forest.large_data_directory())

    def test_create_forest(self):
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))

        host = Host.list(conn)[0]

        forest = Forest("test-forest-simple-create", host=host)

        forest.set_large_data_directory(ds.large_data_directory)
        forest.set_fast_data_directory(ds.fast_data_directory)

        forest.create(conn)

        forest = Forest.lookup(conn, "test-forest-simple-create")

        try:
            self.assertIsNotNone(forest)
            self.assertEqual("test-forest-simple-create", forest.forest_name())
            self.assertEqual(host, forest.host())
            self.assertEqual(ds.large_data_directory, forest.large_data_directory())
            self.assertEqual(ds.fast_data_directory, forest.fast_data_directory())
        finally:
            forest.delete(connection=conn)

if __name__ == "__main__":
    unittest.main();
