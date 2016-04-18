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
# Norman Walsh      04/29/2015     Hacked role.py into privilege.py
#

"""
Classes for manipulating MarkLogic privileges.
"""

from __future__ import unicode_literals, print_function, absolute_import
import json
import logging
from marklogic.exceptions import UnexpectedManagementAPIResponse
from marklogic.models.model import Model
from marklogic.utilities.validators import validate_custom
from marklogic.utilities.validators import validate_privilege_kind
from marklogic.utilities import PropertyLists


class Privilege(Model, PropertyLists):
    """
    The Privilege class encapsulates a MarkLogic privilege.
    """
    PRIVLIST = None

    def __init__(self, name, kind, action=None,
                 connection=None, save_connection=True):
        validate_privilege_kind(kind)

        self._config = {}
        self._config['privilege-name'] = name
        self._config['action'] = action
        self.the_kind = kind
        self.etag = None
        self.name = name
        self.logger = logging.getLogger("marklogic.privilege")
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None

    def privilege_name(self):
        """
        Return the name of the privilege.

        :return: The privilege name
        """
        return self._get_config_property('privilege-name')

    def set_privilege_name(self, name):
        """
        Set the name of the privilege.

        :return: The privilege object
        """
        self._config['privilege-name'] = name
        return self

    def action(self):
        """
        Return the action URI of the privilege.

        :return: The privilege action
        """
        return self._get_config_property('action')

    def set_action(self, action):
        """
        Set the action URI of the privilege.

        :return: The privilege object
        """
        self._config['action'] = action
        return self

    def kind(self):
        """
        Return the kind of privilege.

        :return: The privilege kind
        """
        return self.the_kind

    def set_kind(self, kind):
        """
        Set the action URI of the privilege.

        :return: The privilege object
        """
        validate_privilege_kind(kind)
        self.the_kind = kind
        return self

    def role_names(self):
        """
        Returns the role names for this privilege

        :return: The list of role names
        """
        return self._get_config_property('role')

    def set_role_names(self, roles):
        """
        Sets the roles for this privilege

        :return: The privilege object
        """
        return self.set_property_list('role', roles)

    def add_role_name(self, add_role):
        """
        Adds the specified role to roles for this privilege

        :return: The privilege object
        """
        return self.add_to_property_list('role', add_role)

    def remove_role_name(self, remove_role):
        """
        Removes the specified role to roles for this privilege

        :return: The privilege object
        """
        return self.remove_from_property_list('role', remove_role)

    def marshal(self):
        """Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values,
        recursively.
        """
        struct = {}
        for key in self._config:
            struct[key] = self._config[key]
        return struct

    @classmethod
    def unmarshal(cls, config, connection=None, save_connection=True):
        """Construct a new Privilege from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties :return: A newly
        constructed Privilege object with the specified properties.
        """
        kind = config['kind']
        validate_privilege_kind(kind)

        result = Privilege("temp", kind, "http://example.com/",
                           connection=connection,
                           save_connection=save_connection)

        result._config = config
        result.name = config['privilege-name']
        result.the_kind = kind
        return result

    def create(self, connection=None):
        """
        Creates the Privilege on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Privilege object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("privileges")

        post_config = self._config
        post_config['kind'] = self.kind()

        response = connection.post(uri, payload=post_config)
        return self

    def read(self, connection=None):
        """
        Loads the Privilege from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The Privilege object
        """
        if connection is None:
            connection = self.connection

        priv = Privilege.lookup(connection, self.privilege_name(), self.kind())
        if priv is None:
            return None
        else:
            self._config = priv._config
            self.etag = priv.etag
            return self

    def update(self, connection=None):
        """
        Updates the Privilege on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Privilege object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("privileges", self.name,
                             parameters=["kind="+self.kind()])

        response = connection.put(uri, payload=self._config, etag=self.etag)

        self.name = self._config['privilege-name']
        if 'etag' in response.headers:
                self.etag = response.headers['etag']

        return self

    def delete(self, connection=None):
        """
        Deletes the Privilege from the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Privilege object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("privileges", self.name, properties=None,
                             parameters=["kind="+self.kind()])

        response = connection.delete(uri, etag=self.etag)
        return self

    @classmethod
    def list(cls, connection, kind=None, include_actions=False):
        """
        List all the privilege names. Privilege names are structured values,
        they consist of a kind and a name separated by "|".

        If `include_actions` is true, the structured values consist of
        kind, name, and action separated by "|".

        :param connection: The connection to a MarkLogic server
        :return: A list of Privilege names.
        """

        uri = connection.uri("privileges")
        response = connection.get(uri)

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['privilege-default-list']['list-items']['list-item']:
            if kind is None:
                if include_actions:
                    results.append("{0}|{1}|{2}"
                                   .format(item['kind'], item['nameref'],
                                           item['action']))
                else:
                    results.append("{0}|{1}"
                                   .format(item['kind'], item['nameref']))
            else:
                if item['kind'] == kind:
                    if include_actions:
                        results.append("{1}|{2}"
                                       .format(item['nameref'],
                                               item['action']))
                    else:
                        results.append(item['nameref'])

        return results

    def exists(self, connection=None):
        """
        Returns true if (and only if) the specified privilege exists.

        If the name is a structured value consisting of the kind and the
        name separated by a "|", as returned by the list() method, then
        the kind is optional.

        :param connection: The connection to the MarkLogic database
        :return: The privilege
        """
        if connection is None:
            connection = self.connection

        parameters = []
        if self.kind() is not None:
            parameters = ["kind=" + self.kind()]
        uri = connection.uri("privileges", self.privilege_name(),
                             parameters=parameters)

        response = connection.head(uri)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise UnexpectedManagementAPIResponse(response.text)

    @classmethod
    def lookup(cls, connection, name=None, kind=None, action=None):
        """
        Look up an individual privilege.

        At least one of name or action must be specified. Privileges can
        be looked up directly with a name. If only an action is provided,
        the method will get the current list of privileges and search for
        the matching action. The list of privileges is stored in
        `Privilege.PRIVLIST` and can be reset by calling
        `Privilege.flush_cache()`.

        The `kind` must be provided either directly or as part of a
        structured name.

        If the name is a structured value consisting of the kind and the
        name separated by a "|", as returned by the list() method, then
        the kind is optional.

        :param connection: The connection to the MarkLogic database
        :param name: The name of the privilege
        :param action: The action URI of the privilege
        :param kind: The kind of privilege
        :return: The privilege
        """
        if name is not None:
            parts = name.split("|")
            if len(parts) == 1:
                pass
            elif len(parts) == 2 or len(parts) == 3:
                if kind is not None and kind != parts[0]:
                    raise validate_custom("Kinds must match")
                kind = parts[0]
                name = parts[1]
                if action is not None and len(parts) == 3:
                    if parts[2] != action:
                        raise validate_custom("Actions must match")
            else:
                raise validate_custom("Unparseable privilege name")

        if name is None and action is None:
            raise validate_custom("Name or action must be specified")

        if kind is None:
            raise validate_custom("Kind must be specified")

        if name is None:
            return cls._lookup_action(connection, action, kind)
        else:
            uri = connection.uri("privileges", name, parameters=["kind="+kind])
            response = connection.get(uri)
            if response.status_code == 200:
                result = Privilege.unmarshal(json.loads(response.text))
                if 'etag' in response.headers:
                    result.etag = response.headers['etag']
                return result
            else:
                return None

    @classmethod
    def _lookup_action(cls, conn, action, kind):
        if Privilege.PRIVLIST is None:
            Privilege.PRIVLIST = Privilege.list(conn, include_actions=True)

        for priv in Privilege.PRIVLIST:
            parts = priv.split("|")
            if parts[0] == kind and parts[2] == action:
                return cls.lookup(conn, parts[1], kind)

        return None

    @classmethod
    def flush_cache(cls):
        """
        Reset the cache of saved privileges.
        """
        Privilege.PRIVLIST = None
