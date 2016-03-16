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
# Paul Hoehne       03/05/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models import Database
from marklogic.models.database.path import PathNamespace

class TestDbPaths(MLConfig):

    def test_create_paths(self):
        db = Database(u'testdb')

        assert 'path-namespaces' not in db._config
        return_val = db.add_path_namespace(PathNamespace("inv", "http://foo.bar.com/invoice"))

        namespaces = db.path_namespaces()
        assert 1 == len(namespaces)
        assert "inv" == namespaces[0].prefix()
        assert 'http://foo.bar.com/invoice' == namespaces[0].namespace_uri()

        assert db == return_val
