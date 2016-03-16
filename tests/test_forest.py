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
# Paul Hoehne       03/28/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models import Forest, Host
from marklogic.utilities.validators import ValidationError

class TestForest(MLConfig):
    def test_forest_defaults(self):
        pass

    def test_getters_and_setters(self):
        forest = Forest("Foo", host="bar")
        forest.set_data_directory("")
        forest.set_large_data_directory("")
        forest.set_fast_data_directory("")

        assert "Foo" == forest.forest_name()

        forest.set_availability("offline")
        assert "offline" == forest.availability()

        try:
            forest.set_availability("foo")
            assert False
        except ValidationError:
            assert True

        assert "bar" == forest.host()

        assert "" == forest.data_directory()

        assert "" == forest.fast_data_directory()

        assert "" == forest.large_data_directory()

    def test_create_forest(self):
        host = Host.list(self.connection)[0]

        forest = Forest("test-forest-simple-create", host=host)

        forest.set_large_data_directory("")
        forest.set_fast_data_directory("")

        forest.create(self.connection)

        forest = Forest.lookup(self.connection, "test-forest-simple-create")

        try:
            assert forest is not None
            assert "test-forest-simple-create" == forest.forest_name()
            assert host == forest.host()
            assert "" == forest.large_data_directory()
            assert "" == forest.fast_data_directory()
        finally:
            forest.delete(connection=self.connection)

