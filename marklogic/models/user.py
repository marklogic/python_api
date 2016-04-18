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
# Norman Walsh      08/09/2015     Initial development
#

"""
User related classes for manipulating MarkLogic users
"""

from __future__ import unicode_literals, print_function, absolute_import

import json
from marklogic.models.model import Model
from marklogic.models.permission import Permission
from marklogic.utilities import PropertyLists


class User(Model, PropertyLists):
    """
    The User class encapsulates a MarkLogic user.  It provides
    methods to set/get database attributes.  The use of methods will
    allow IDEs with tooling to provide auto-completion hints.
    """
    def __init__(self, name, password=None, connection=None,
                 save_connection=True):
        self._config = {}
        self._config['user-name'] = name
        if password is not None:
            self._config['password'] = password
        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.name = name

    def role_names(self):
        """
        Returns the roles for this user

        :return: The list of roles
        """
        return self.get_property_list('role')

    def set_role_names(self, roles):
        """
        Sets the roles for this user

        :return: The user object
        """
        return self.set_property_list('role', roles)

    def add_role_name(self, add_role):
        """
        Adds the specified role to roles for this user

        :return: The user object
        """
        return self.add_to_property_list('role', add_role)

    def remove_role_name(self, remove_role):
        """
        Removes the specified role to roles for this user

        :return: The user object
        """
        return self.remove_from_property_list('role', remove_role)

    def permissions(self):
        """
        Returns the permissions for this user

        :return: The list of :class:`marklogic.models.permission.Permission`
        """
        if 'permission' not in self._config:
            return None

        perms = []
        for item in self._config['permission']:
            perm = Permission(item['role-name'], item['capability'])
            perms.append(perm)

        return perms

    def set_permissions(self, perms):
        """
        Sets the permissions for this user

        :return: The user object
        """
        return self.set_property_list('permission', perms, Permission)

    def add_permission(self, perm):
        """
        Adds the specified permission to the list of permissions for this user

        :return: The user object
        """
        return self.add_to_property_list('permission', perm, Permission)

    def remove_permission(self, perm):
        """
        Removes the specified permission from the permissions for this user

        :param perm: The permission to remove

        :return: The user object
        """
        return self.remove_from_property_list('permission', perm, Permission)

    def collections(self):
        """
        Returns the collections for this user

        :return: The list of collections
        """
        return self._get_config_property('collection')

    def set_collections(self, collections):
        """
        Sets the collections for this user

        :return: The user object
        """
        return self.set_property_list('collection', collections)

    def add_collection(self, collection):
        """
        Adds the specified collection to the list of collections for this user

        :return: The user object
        """
        return self.add_to_property_list('collection', collection)

    def remove_collection(self, collection):
        """
        Removes the specified collection from the collections for this user

        :param perm: The collection to remove

        :return: The user object
        """
        return self.remove_from_property_list('collection', collection)

    def external_names(self):
        """
        Returns the external_names for this user

        :return: The list of external_names
        """
        return self._get_config_property('external-name')

    def set_external_names(self, names):
        """
        Sets the external names for this user

        :param: names: The external names
        :return: The user object
        """
        return self.set_property_list('external-name', names)

    def add_external_name(self, name):
        """
        Adds the specified external name to the list of external
        names for this user

        :param: name: The external name
        :return: The user object
        """
        return self.add_to_property_list('external-name', name)

    def remove_external_name(self, name):
        """
        Removes the specified external name from the external
        names for this user

        :param perm: The external name to remove

        :return: The user object
        """
        return self.remove_from_property_list('external-name', name)

    def marshal(self):
        """Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = {}
        for key in self._config:
            struct[key] = self._config[key]
        return struct

    @classmethod
    def unmarshal(cls, config, connection=None, save_connection=True):
        """
        Construct a new User from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed User object with the specified properties.
        """
        result = User("temp",
                      connection=connection, save_connection=save_connection)
        result._config = config
        result.name = config['user-name']
        result.etag = None
        return result

    def exists(self, connection=None):
        """
        Checks to see if the user exists on the server.

        :param connection: The connection to a MarkLogic server
        :return: True if the user exists
        """
        if connection is None:
            connection = self.connection

        user = User.lookup(connection, self.user_name())
        return user is not None

    def create(self, connection=None):
        """
        Creates the User on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("users")
        response = connection.post(uri, payload=self._config)
        return self

    def read(self, connection=None):
        """
        Loads the User from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        if connection is None:
            connection = self.connection

        user = User.lookup(connection, self._config['user-name'])
        if user is None:
            return None
        else:
            self._config = user._config
            self.etag = user.etag
            return self

    def update(self, connection=None):
        """
        Updates the User on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("users", self.name)
        response = connection.put(uri, payload=self._config, etag=self.etag)

        self.name = self._config['user-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def delete(self, connection=None):
        """
        Deletes the User from the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("users", self.name, properties=None)
        response = connection.delete(uri, etag=self.etag)
        return self

    @classmethod
    def list(cls, connection):
        """
        List all the user names.

        :param connection: The connection to a MarkLogic server
        :return: A list of user names
        """

        uri = connection.uri("users")
        response = connection.get(uri)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['user-default-list']['list-items']['list-item']:
            results.append(item['nameref'])

        return results

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up an individual user.

        :param name: The name of the user
        :param connection: The connection to the MarkLogic database
        :return: The user
        """
        uri = connection.uri("users", name)
        response = connection.get(uri)

        if response.status_code == 200:
            result = User.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    # Below this point are machine generated methods for getting
    # and setting atomic values

    def user_name(self):
        """
        The user name.

        :return: The user-name.
        """
        return self._get_config_property('user-name')

    def set_user_name(self, value):
        """
        Set the user-name.

        :param value: The user-name.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('user-name', value)

    def set_password(self, value):
        """
        Set the password.

        :param value: The password.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('password', value)

    def description(self):
        """
        The user description.

        :return: The description.
        """
        return self._get_config_property('description')

    def set_description(self, value):
        """
        Set the description.

        :param value: The description.
        :return: The object with the mutated property value.
        """
        self._validate(value, 'string')
        return self._set_config_property('description', value)
