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
# Paul Hoehne       04/02/2015     Initial development
# Norman Walsh      04/29/2015     Hacked role.py into user.py
#

"""
User related classes for manipulating MarkLogic users
"""

from __future__ import unicode_literals, print_function, absolute_import

import requests
from marklogic.models.utilities import exceptions
from marklogic.models.permission import Permission
from marklogic.models.utilities.utilities import PropertyLists
import json

class User(PropertyLists):
    """
    The User class encapsulates a MarkLogic user.  It provides
    methods to set/get database attributes.  The use of methods will
    allow IDEs with tooling to provide auto-completion hints.
    """
    def __init__(self, name, password=None):
        self._config = {}
        self._config['user-name'] = name
        if password is not None:
            self._config['password'] = password
        self.etag = None
        self.name = name

    def user_name(self):
        """
        Return the name of the user.

        :return: The user name
        """
        return self._config['user-name']

    def set_user_name(self, name):
        """
        Set the name of the user.

        :return: The user object
        """
        self._config['user-name'] = name
        return self

    def set_password(self, psw):
        """
        Set the password of the user.

        There is no method to get the password.

        :return: The user object
        """
        self._config['password'] = psw
        return self

    def description(self):
        """
        Returns the description for the user.

        :return: The user description
        """
        if 'description' not in self._config:
            return None
        return self._config['description']

    def set_description(self, description):
        """
        Set the description for the user

        :param description: A description for the user

        :return: The user object
        """
        self._config['description'] = description
        return self

    def role_names(self):
        """
        Returns the roles for this user

        :return: The list of roles
        """
        if u'role' not in self._config:
            return None
        return self._config[u'role']

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
            perm = Permission(item['role-name'],item['capability'])
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
        if 'collection' not in self._config:
            return None
        return self._config['collection']

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
        if 'external-name' not in self._config:
            return None
        return self._config['external-name']

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
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = { }
        for key in self._config:
            struct[key] = self._config[key];
        return struct

    @classmethod
    def unmarshal(cls, config):
        """
        Construct a new User from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed User object with the specified properties.
        """
        result = User("temp")
        result._config = config
        result.name = config['user-name']
        result.etag = None
        return result

    def create(self, connection):
        """
        Creates the User on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        uri = "http://{0}:{1}/manage/v2/users" \
          .format(connection.host, connection.management_port)

        response = requests.post(uri, json=self._config, auth=connection.auth)

        if response.status_code not in [200, 201, 204]:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        return self

    def read(self, connection):
        """
        Loads the User from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        user = User.lookup(self._config['role-name'])
        if user is None:
            return None
        else:
            self._config = user._config
            self.etag = user.etag
            return self

    def update(self, connection):
        """
        Updates the User on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        uri = "http://{0}:{1}/manage/v2/users/{2}/properties" \
          .format(connection.host, connection.management_port,self.name)

        headers = {}
        if self.etag is not None:
            headers['if-match'] = self.etag

        response = requests.put(uri, json=self._config, auth=connection.auth,
                                headers=headers)

        if response.status_code not in [200, 204]:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        self.name = self._config['user-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def delete(self, connection):
        """
        Deletes the User from the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The User object
        """
        uri = "http://{0}:{1}/manage/v2/users/{2}" \
          .format(connection.host, connection.management_port, self.name)

        headers = {}
        if self.etag is not None:
            headers['if-match'] = self.etag

        response = requests.delete(uri, auth=connection.auth, headers=headers)

        if (response.status_code not in [200, 204]
            and not response.status_code == 404):
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        return self

    @classmethod
    def list(cls, connection):
        """
        List all the user names.

        :param connection: The connection to a MarkLogic server
        :return: A list of user names
        """

        uri = "http://{0}:{1}/manage/v2/users" \
          .format(connection.host, connection.management_port)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code != 200:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

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
        uri = "http://{0}:{1}/manage/v2/users/{2}/properties".format(connection.host, connection.port,
                                                                     name)
        response = requests.get(uri, auth=connection.auth, headers={'accept': 'application/json'})

        if response.status_code == 200:
            result = User.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        elif response.status_code == 404:
            return None
        else:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)
