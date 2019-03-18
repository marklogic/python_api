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
# Paul Hoehne       03/26/2015     Initial development
# Norman Walsh      05/02/2018     Adapted from test_host.py
#

from mlconfig import MLConfig
from marklogic.models.group import Group

class TestGroup(MLConfig):
    def group_list(self):
        return Group.list(self.connection)

    def test_list_groups(self):
        groups = self.group_list()
        assert len(groups) > 0
        assert groups

    def test_load(self):
        group_name = self.group_list()[0]
        group = Group(group_name)
        assert group.read(self.connection) is not None
        assert group.host_timeout() > 0

