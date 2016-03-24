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
# Norman Walsh      24 Mar 2016    Initial development
#

from mlconfig import MLConfig
from marklogic.models.amp import Amp
from marklogic.exceptions import UnexpectedManagementAPIResponse

class TestAmp(MLConfig):
    def test_list_amps(self):
        amps = Amp.list(self.connection)
        assert len(amps) > 100

    def test_create_amp(self):
        beforeAmps = Amp.list(self.connection)
        amp = Amp("test-amp", "http://example.com", "/MarkLogic/test-amp.xqy", \
              connection=self.connection)

        amp.create()
        afterAmps = Amp.list(self.connection)
        assert len(afterAmps) > len(beforeAmps)
        newAmp = Amp.lookup(self.connection, amp.local_name(), \
                                amp.namespace(), amp.document_uri())
        assert isinstance(newAmp, Amp)

        for key in amp._config:
            assert newAmp._config[key] == amp._config[key]

        amp.set_role_names(["manage-admin"])
        amp.update(connection=self.connection)

        newAmp.set_document_uri("/MarkLogic/no-can-do")
        try:
            newAmp.update(connection=self.connection)
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        amp.delete()
        afterAmps = Amp.list(self.connection)
        assert len(afterAmps) == len(beforeAmps)
        newAmp = Amp.lookup(self.connection, amp.local_name(), \
                                amp.namespace(), amp.document_uri())
        assert newAmp is None
