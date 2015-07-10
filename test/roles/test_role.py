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
# Paul Hoehne       04/03/2015     Initial development
#

import unittest
from marklogic.models import Connection, Role, Privilege
from test.resources import TestConnection as tc

class TestRole(unittest.TestCase):

    def test_list(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        names = Role.list(connection)

        self.assertGreater(len(names), 65)
        self.assertIn("admin", names)

    def test_lookup(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        role = Role.lookup(connection, "admin")

        self.assertIsNotNone(role)
        self.assertEqual(role.role_name(), "admin")

    def test_create_role(self):
        new_role = Role("foo-role")

        self.assertEqual(new_role.role_name(), "foo-role")

        new_role.add_role_name("admin")
        self.assertIn("admin", new_role.role_names())

    def test_description(self):
        role = Role("foo-role")
        role.set_description("This is the foo role")

        self.assertEqual(role.description(), "This is the foo role")

    def test_add_privilege(self):
        role = Role("foo-role")

        name = "foodle"
        action = "http://marklogic.com/xdmp/privileges/foodle"
        kind = "execute"

        role.add_privilege(name, kind)

        priv = role.privileges()[0]
        self.assertEqual("execute|foodle",priv)

    def test_create_remove_role(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        role = Role("foo-role")

        role.create(connection)

        the_role = Role.lookup(connection, "foo-role")
        self.assertIsNotNone(the_role)

        the_role.delete(connection)
        the_role = Role.lookup(connection, "foo-role")
        self.assertIsNone(the_role)

    def test_save_role(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        role = Role("foo-role")

        self.assertIsNone(role.create(connection).description())
        role.set_description("This is the foo role")

        role.update(connection)

        role = Role.lookup(connection, "foo-role")
        self.assertEqual("This is the foo role", role.description())

        role.delete(connection)

    def test_roles(self):
        role = Role("foo-role")

        role.add_role_name("bar-role")
        role.add_role_name("baz-role")

        self.assertEqual(2, len(role.role_names()))
        self.assertTrue("bar-role" in role.role_names())
        self.assertTrue("baz-role" in role.role_names())

    def test_privileges(self):
        role = Role("foo-role")

        role.add_privilege("bar-priv", "execute")
        role.add_privilege("baz-priv", "execute")

        self.assertEqual(2, len(role.privileges()))
        self.assertEqual("execute|bar-priv", role.privileges()[0])

if __name__ == "__main__":
    unittest.main()
