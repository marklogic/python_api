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
# Paul Hoehne       04/03/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models import Role, Privilege

class TestRole(MLConfig):

    def test_list(self):
        names = Role.list(self.connection)

        assert len(names) > 65
        assert "admin" in names

    def test_lookup(self):
        role = Role.lookup(self.connection, "admin")

        assert role is not None
        assert "admin" == role.role_name()

    def test_create_role(self):
        new_role = Role("foo-role")

        assert "foo-role" == new_role.role_name()

        new_role.add_role_name("admin")
        assert "admin" in new_role.role_names()

    def test_description(self):
        role = Role("foo-role")
        role.set_description("This is the foo role")

        assert "This is the foo role" == role.description()

    def test_add_privilege(self):
        role = Role("foo-role")

        name = "foodle"
        action = "http://marklogic.com/xdmp/privileges/foodle"
        kind = "execute"

        role.add_privilege(name, kind)

        priv = role.privileges()[0]
        assert "execute|foodle" == priv

    def test_create_remove_role(self):
        role = Role("foo-role")

        role.create(self.connection)

        the_role = Role.lookup(self.connection, "foo-role")
        assert the_role is not None

        the_role.delete(self.connection)
        the_role = Role.lookup(self.connection, "foo-role")
        assert the_role is None

    def test_save_role(self):
        role = Role("foo-role")

        assert role.create(self.connection).description() is None
        role.set_description("This is the foo role")

        role.update(self.connection)

        role = Role.lookup(self.connection, "foo-role")
        assert "This is the foo role" == role.description()

        role.delete(self.connection)

    def test_roles(self):
        role = Role("foo-role")

        role.add_role_name("bar-role")
        role.add_role_name("baz-role")

        assert 2 == len(role.role_names())
        assert "bar-role" in role.role_names()
        assert "baz-role" in role.role_names()

    def test_privileges(self):
        role = Role("foo-role")

        role.add_privilege("bar-priv", "execute")
        role.add_privilege("baz-priv", "execute")

        assert 2 == len(role.privileges())
        assert "execute|bar-priv" == role.privileges()[0]
