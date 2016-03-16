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
from marklogic.models.user import User

class TestUser(MLConfig):
    def test_list(self):
        users = User.list(self.connection)

        assert len(users) > 2
        assert "nobody" in users

    def test_lookup(self):
        user = User.lookup(self.connection, "nobody")

        assert user is not None
        assert "nobody" == user.user_name()

    def test_create_user(self):
        new_user = User("foo-user", "password")

        assert "foo-user" == new_user.user_name()

        new_user.create(self.connection)

        users = User.list(self.connection)

        assert "foo-user" in users
        new_user.delete(self.connection)

    def test_description(self):
        user = User("foo-user")
        user.set_description("This is the foo user")

        assert "This is the foo user" == user.description()

    def test_add_role_name(self):
        user = User("foo-user")

        user.add_role_name(u'manage-user')

        role = user.role_names()[0]
        assert u'manage-user' == role

    def test_create_remove_user(self):
        user = User("foo-user", "password")

        user.create(self.connection)

        the_user = User.lookup(self.connection, "foo-user")
        assert the_user is not None

        the_user.delete(self.connection)
        the_user = User.lookup(self.connection, "foo-user")
        assert the_user is None

    def test_save_user(self):
        user = User("foo-user", "password")

        assert user.create(self.connection).description() is None
        user.set_description("This is the foo user")

        user.update(self.connection)

        user = User.lookup(self.connection, "foo-user")
        assert "This is the foo user" == user.description()

        user.delete(self.connection)

