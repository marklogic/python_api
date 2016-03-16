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

from mlconfig import MLConfig
from marklogic.models.certificate.request import Request
from marklogic.models.certificate.template import Template

class TestCertRequest(MLConfig):
    def test_template(self):
        req = Request(countryName="US", stateOrProvinceName="TX",
                      localityName="Austin", organizationName="MarkLogic",
                      emailAddress="Norman.Walsh@marklogic.com",
                      version=0)
        temp = Template("Test Template", "Test description", req)

        assert "Test Template" == temp.template_name()

        temp.create(self.connection)

        names = Template.list(self.connection)

        assert len(names) > 0
        assert temp.template_id() in names

        temp.set_template_name("New Name")
        temp.set_template_description("New Description")
        temp.update(self.connection)
        assert temp is not None

        newtemp = Template.lookup(self.connection, temp.template_id())
        assert temp.template_name() == newtemp.template_name()

        temp.delete(self.connection)

        assert temp is not None
