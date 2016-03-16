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
# Norman Walsh      05/01/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models import Role, Privilege

class TestPrivilege(MLConfig):

    def test_list(self):
        privileges = Privilege.list(self.connection)

        assert len(privileges) > 300
        assert "execute|manage-admin" in privileges

    def test_lookup(self):
        privilege = Privilege.lookup(self.connection,
                                     name="manage-admin", kind="execute")

        assert privilege is not None
        assert "manage-admin" == privilege.privilege_name()

    def test_lookup_action(self):
        privilege = Privilege.lookup(self.connection, kind="execute",
                action="http://marklogic.com/xdmp/privileges/admin-module-write")

        assert privilege is not None
        assert "admin-module-write" == privilege.privilege_name()

    def test_create_privilege(self):
        new_privilege = Privilege("foo-privilege",kind="execute",
                                  action="http://example.com/")

        assert "foo-privilege" == new_privilege.privilege_name()

        new_privilege.create(self.connection)

        privileges = Privilege.list(self.connection)
        assert "execute|foo-privilege" in privileges

        new_privilege.delete(self.connection)

    def test_add_role(self):
        privilege = Privilege("foo-privilege", kind="execute",
                              action="http://example.com/")

        privilege.add_role_name(u'manage-admin')

        role = privilege.role_names()[0]
        assert u'manage-admin' == role

    def test_create_remove_privilege(self):
        privilege = Privilege("foo-privilege", kind="execute",
                              action="http://example.com/")

        privilege.create(self.connection)

        the_privilege = Privilege.lookup(self.connection, kind="execute",
                                         action="http://example.com/")
        assert the_privilege is not None

        the_privilege.delete(self.connection)
        the_privilege = Privilege.lookup(self.connection, kind="execute",
                                         action="foo-privilege")
        assert the_privilege is None

    def test_save_privilege(self):
        privilege = Privilege("foo-privilege", kind="execute",
                              action="http://example.com/")
        privilege.create(self.connection)

        privilege.add_role_name("manage-user")
        privilege.update(self.connection)

        assert "manage-user" in  privilege.role_names()

        privilege.delete(self.connection)
