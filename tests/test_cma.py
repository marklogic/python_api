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

import json
from mlconfig import MLConfig
from marklogic.client.cma import CMA
from marklogic.models import Database

class TestCMA(MLConfig):

    def test_generate_config(self):
        cma = CMA(self.connection)
        cma.format="xml"
        config = cma.generate_config()
        assert config is not None
        assert json.dumps(config)[1] == '<'
        cma.format = "json"
        config = cma.generate_config()
        assert config is not None
        assert json.dumps(config)[1] == '{'

    def test_apply_config(self):
        cma = CMA(self.connection)
        config1 = {
            "config": [
                {
                    "database": [
                        {
                            "database-name": "CMA_Check1"
                        }
                    ]
                }
            ]
        }
        config2 = "<configuration xmlns=\"http://marklogic.com/manage/config\"><configs><config><databases><database><database-name>CMA_Check2</database-name></database></databases></config></configs></configuration>"
        cma.apply_config(json.dumps(config1), "application/json")
        cma.apply_config(config2, "application/xml")

        validate_db1 = Database.lookup(self.connection, "CMA_Check1")
        try:
            assert validate_db1 is not None
            assert 'CMA_Check1' == validate_db1.database_name()

        finally:
            validate_db1.delete(connection=self.connection)
            validate_db1 = Database.lookup(self.connection, "CMA_Check1")
            assert validate_db1 is None

        validate_db2 = Database.lookup(self.connection, "CMA_Check2")
        try:
            assert validate_db2 is not None
            assert 'CMA_Check2' == validate_db2.database_name()

        finally:
            validate_db2.delete(connection=self.connection)
            validate_db2 = Database.lookup(self.connection, "CMA_Check2")
            assert validate_db2 is None