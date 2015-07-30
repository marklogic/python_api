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
# Norman Walsh      05/01/2015     Initial development
#

import unittest
from marklogic.connection import Connection
from marklogic.models import Role, Privilege
from test.resources import TestConnection as tc

class TestPrivilege(unittest.TestCase):

    def test_list(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        privileges = Privilege.list(connection)

        self.assertGreater(len(privileges), 300)
        self.assertIn("execute|manage-admin", privileges)

    def test_lookup(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        privilege = Privilege.lookup(connection, "manage-admin", "execute")

        self.assertIsNotNone(privilege)
        self.assertEqual(privilege.privilege_name(), "manage-admin")

    def test_lookup_action(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)

        privilege = Privilege.lookup(connection, kind="execute", \
          action="http://marklogic.com/xdmp/privileges/admin-module-write")

        self.assertIsNotNone(privilege)
        self.assertEqual(privilege.privilege_name(), "admin-module-write")

    def test_create_privilege(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        new_privilege = Privilege("foo-privilege","http://example.com/","execute")

        self.assertEqual(new_privilege.privilege_name(), "foo-privilege")

        new_privilege.create(connection)

        privileges = Privilege.list(connection)
        self.assertIn("execute|foo-privilege", privileges)

        new_privilege.delete(connection)

    def test_add_role(self):
        privilege = Privilege("foo-privilege","http://example.com/","execute")

        privilege.add_role_name(u'manage-admin')

        role = privilege.role_names()[0]
        self.assertEqual(u'manage-admin', role)

    def test_create_remove_privilege(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        privilege = Privilege("foo-privilege","http://example.com/","execute")

        privilege.create(connection)

        the_privilege = Privilege.lookup(connection, "foo-privilege", "execute")
        self.assertIsNotNone(the_privilege)

        the_privilege.delete(connection)
        the_privilege = Privilege.lookup(connection, "foo-privilege", "execute")
        self.assertIsNone(the_privilege)

    def test_save_privilege(self):
        connection = Connection.make_connection(tc.hostname, tc.admin, tc.password)
        privilege = Privilege("foo-privilege","http://example.com/","execute")
        privilege.create(connection)

        privilege.add_role_name("manage-user")
        privilege.update(connection)

        self.assertIn("manage-user", privilege.role_names())

        privilege.delete(connection)

if __name__ == "__main__":
    unittest.main()
