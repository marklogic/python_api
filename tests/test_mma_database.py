# -*- coding: utf-8 -*-
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

from mlconfig import MLConfig
from marklogic import MarkLogic
from marklogic.mma import MMA

class TestMmaDatabase(MLConfig):
    def test_create_database(self):
        self.marklogic = MarkLogic(self.connection)
        dbname = 'test-mma-database'

        mma = MMA(self.connection)
        mma.run(['create', 'database', dbname])

        assert dbname in self.marklogic.databases()

        mma.run(['delete', 'database', dbname])

        assert dbname not in self.marklogic.databases()

