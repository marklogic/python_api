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
#

"""
Role related classes for manipulating MarkLogic roles
"""

from __future__ import unicode_literals, print_function, absolute_import

import requests
from marklogic.models.utilities import exceptions
from marklogic.models.utilities.utilities import PropertyLists
import json

class Role(PropertyLists):
    """
    The Role class encapsulates a MarkLogic role.  It provides
    methods to set/get database attributes.  The use of methods will
    allow IDEs with tooling to provide auto-completion hints.
    """

    def __init__(self, name):
        self._config = {}
        self._config['role-name'] = name
        self.name = name
        self.etag = None

    def role_name(self):
        """
        The Role name (unique)

        *role name* is the name of the role.

        :return: The role name
        """
        return self._config['role-name']

    def set_role_name(self, name):
        """
        Sets the Role name (unique)

        *role name* is the name of the role.

        :param: The new role name

        :return: The role object
        """
        return self._config['role-name']

    def compartment(self):
        """
        The compartment that this role is part of.

        A *compartment* is an optional field that places the
        role into the named compartment. If a document has
        any permissions (role/capability pairs) with roles
        that have a compartment, then the user must have those
        roles with each of the compartments (regardless of
        which permission they are in) to perform any of the
        capabilities.

        Once set, the compartment name cannot be changed.

        :return: The compartment name
        """
        if 'compartment' in self._config:
            return self._config['compartment']
        return None

    def role_names(self):
        """
        Returns the names of the roles assigned to this role

        :return: The list of roles
        """
        if "role" not in self._config:
            return None
        return self._config['role']

    def set_role_names(self, roles):
        """
        Sets the names of the roles assigned to this role

        :return: The role object
        """
        return self.set_property_list('role', roles)

    def add_role_name(self, add_role):
        """
        Adds the specified role to roles assigned to this role

        :return: The role object
        """
        return self.add_to_property_list('role', add_role)

    def remove_role_name(self, remove_role):
        """
        Removes the specified role from the roles assigned to this role

        :return: The role object
        """
        return self.remove_from_property_list('role', remove_role)

    def set_description(self, description):
        """
        Sets an object's description.

        *description* is an optional field to describe the
        user.

        :param description: A description for the role

        :return: The role object
        """
        self._config['description'] = description
        return self

    def description(self):
        """
        An object's description.

        *description* is an optional field to describe the
        user.

        :return: The role description
        """
        if 'description' not in self._config:
            return None
        return self._config['description']

    def add_privilege(self, name, kind=None):
        """
        Add a new privilege to the list of role privileges.

        If the name is a structured value consisting of the kind and the
        name separated by a "|", as returned by the list() method, then
        the kind is optional.

        :param name: The name of the privilege
        :param kind: The kind of privilege

        :return: The role object
        """
        parts = name.split("|")
        if len(parts) == 1:
            pass
        elif len(parts) == 2:
            if kind is not None and kind != parts[0]:
                raise validate_custom("Kinds must match")
            kind = parts[0]
            name = parts[1]
        else:
            raise validate_custom("Unparseable privilege name")

        key = "{0}|{1}".format(kind,name)
        return self.add_to_property_list('privilege', key)

    def set_privileges(self, names):
        """
        Set the list of privileges associates with this role.

        The names must be structured values consisting of the kind and the
        name separated by a "|", as returned by the list() method.

        :param names: The structure names of the privileges

        :return: The role object
        """
        for name in names:
            parts = name.split("|")
            if len(parts) == 1:
                pass
            elif len(parts) == 2:
                if kind is not None and kind != parts[0]:
                    raise validate_custom("Kinds must match")
                kind = parts[0]
                name = parts[1]
            else:
                raise validate_custom("Unparseable privilege name")
        return self.set_property_list('privilege', names)

    def remove_privilege(self, name, kind=None):
        """
        Remove a privilege from the list of role privileges.

        If the name is a structured value consisting of the kind and the
        name separated by a "|", as returned by the list() method, then
        the kind is optional.

        :param name: The name of the privilege
        :param kind: The kind of privilege

        :return: The role object
        """
        parts = name.split("|")
        if len(parts) == 1:
            pass
        elif len(parts) == 2:
            if kind is not None and kind != parts[0]:
                raise validate_custom("Kinds must match")
            kind = parts[0]
            name = parts[1]
        else:
            raise validate_custom("Unparseable privilege name")

        key = "{0}|{1}".format(kind,name)
        return self.remove_from_property_list('privilege', key)

    def privileges(self):
        """
        Returns the privileges for a given role

        :return: The list of privileges
        """
        if 'privilege' not in self._config:
            return None
        return self._config['privilege']

    @classmethod
    def unmarshal(cls, config):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        result = Role("temp")
        result._config = config
        result.name = config['role-name']
        result.etag = None
        return result

    def marshal(self):
        """
        Construct a new Role from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed Role object with the specified properties.
        """
        struct = { }
        for key in self._config:
            struct[key] = self._config[key];
        return struct

    def create(self, connection):
        """
        Creates the Role on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Role object
        """
        uri = "http://{0}:{1}/manage/v2/roles" \
          .format(connection.host, connection.management_port)

        response = requests.post(uri, json=self._config, auth=connection.auth)
        if response.status_code not in [200, 201, 204]:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        return self

    def read(self, connection):
        """
        Loads the Role from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The Role object
        """
        role = Role.lookup(connection, self._config['role-name'])
        if role is None:
            return None
        else:
            self._config = role._config
            self.etag = role.etag
            return self

    def update(self, connection):
        """
        Updates the Role on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Role object
        """
        uri = "http://{0}:{1}/manage/v2/roles/{2}/properties" \
          .format(connection.host, connection.management_port,self.name)

        headers = {}
        if self.etag is not None:
            headers['if-match'] = self.etag

        response = requests.put(uri, json=self._config, auth=connection.auth,
                                headers=headers)

        if response.status_code not in [200, 204]:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        self.name = self._config['role-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def delete(self, connection):
        """
        Deletes the Role from the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Role object
        """
        uri = "http://{0}:{1}/manage/v2/roles/{2}" \
          .format(connection.host, connection.management_port, self.name)

        response = requests.delete(uri, auth=connection.auth)

        if (response.status_code not in [200, 204]
            and not response.status_code == 404):
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        return self

    @classmethod
    def list(cls, connection):
        """
        List all the roles names.

        :param connection: The connection to a MarkLogic server
        :return: A list of Roles
        """

        uri = "http://{0}:{1}/manage/v2/roles" \
          .format(connection.host, connection.management_port)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code != 200:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['role-default-list']['list-items']['list-item']:
            results.append(item['nameref'])

        return results

    @classmethod
    def exists(cls, connection, name):
        """
        Returns true if (and only if) the specified role exits.

        :param connection: The connection to the MarkLogic database
        :param name: The name of the role
        :return: The role
        """
        uri = "http://{0}:{1}/manage/v2/roles/{2}/properties" \
          .format(connection.host, connection.management_port, name)

        response = requests.head(uri, auth=connection.auth,
                                 headers={'accept': 'application/json'})

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)

    @classmethod
    def lookup(cls, connection, name):
        """
        Look up an individual role.

        :param connection: The connection to the MarkLogic database
        :param name: The name of the role
        :return: The role
        """
        uri = "http://{0}:{1}/manage/v2/roles/{2}/properties" \
          .format(connection.host, connection.management_port, name)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code == 200:
            result = Role.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        elif response.status_code == 404:
            return None
        else:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)
