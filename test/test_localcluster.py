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

import unittest, logging
from marklogic.connection import Connection
from marklogic.models.cluster import LocalCluster
from test.resources import TestConnection as tc

class TestLocalCluster(unittest.TestCase):
    def test_lookup(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        cluster = LocalCluster.lookup(connection)
        self.assertIsNotNone(cluster)

    def test_status_view(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        cluster = LocalCluster(connection=connection)
        status = cluster.view("status")
        self.assertIsNotNone(status)

    def test_version(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        cluster = LocalCluster(connection=connection)
        status = cluster.view("status")
        version = status["local-cluster-status"]["version"]
        self.assertIsNotNone(version)

if __name__ == "__main__":
    unittest.main()
