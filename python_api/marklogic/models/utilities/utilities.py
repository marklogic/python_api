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
# Paul Hoehne       03/05/2015     Initial development
#

"""
Various utility classes.
"""

from __future__ import unicode_literals, print_function, absolute_import
from abc import ABCMeta, abstractmethod
from marklogic.models.utilities.validators import validate_type
from marklogic.models.utilities.validators import validate_list_of_type
from marklogic.models.utilities.validators import assert_list_of_type

class PropertyLists:
    """
    The PropertyLists class is an abstract, mixin class. It defines
    methods for adding, removing and setting the values of a list
    property on an object.
    """
    __metaclass__ = ABCMeta

    def _add_to_object_list(self, objlist, obj, objtype):
        """
        Adds a value to a list of objects.

        The `obj` and any objects in the `objlist`
        must be instances of that type. The `objlist` may be None.

        If `obj` is not currently a member of the list, it is appended
        to the list. If it is already a member, the list returned will
        have the same members as the original list.

        :param: objlist: A list of objects, possibly None
        :param: obj: An object
        :param: objtype: The required type of the objects and the list
        :return: The updated list.
        """
        validate_type(obj,objtype)

        found = False
        newlist = []
        if objlist is not None:
            validate_list_of_type(objlist, objtype)
            for item in objlist:
                found = found or item is obj
                newlist.append(item)
        if not found:
            newlist.append(obj)
        return newlist

    def _add_to_atomic_list(self, atomlist, atom):
        """
        Adds a value to a list of atomic values.

        If `atom` is not currently a member of the list, it is appended
        to the list. If it is already a member, the list returned will
        have the same members as the original list.

        :param: atomlist: A list of atomic values
        :param: atom: An atomic value
        :return: The updated list.
        """
        found = False
        newlist = []
        if atomlist is not None:
            for item in atomlist:
                found = found or item == atom
                newlist.append(item)
        if not found:
            newlist.append(atom)
        return newlist

    def add_to_property_list(self, propname, theitem, thetype=None):
        """
        Adds an item to a configuration property list.

        The `propname` is the name of a property list.

        If `thetype` is not specified, the the list is assumed to be of
        atomic values. Otherwise, `theitem` must be instance of
        `thetype`.

        If `theitem` is not currently a member of the list, it is appended
        to the list. If it is already a member, the list returned will
        have the same members as the original list.

        Atomic values are considered equal if they compare `==`. Objects
        are considered equal if they are the same object.

        :param: propname: The name of a configuration property list
        :param: theitem: An object
        :param: thetype: The required type of the objects and the list or None
        :return: The calling object
        """
        if propname in self._config:
            thelist = self._config[propname]
        else:
            thelist = []

        if thetype is None:
            thelist = self._add_to_atomic_list(thelist, theitem)
        else:
            thelist = self._add_to_object_list(thelist, theitem, thetype)

        if thelist:
            self._config[propname] = thelist
        else:
            if propname in self._config:
                del self._config[propname]

        return self

    def set_property_list(self, propname, objlist, objtype=None):
        """
        Sets the objects in a configuration property list.

        If `objtype` is specified, any objects in the `objlist`
        must be instances of that type. The `objlist` may be empty
        or None.

        :param: objlist: A list of objects
        :param: objtype: The required type of the objects in the list
        :return: The calling object.
        """
        if objlist is None or not objlist:
            thelist = None
        else:
            if objtype is None:
                thelist = objlist
            else:
                thelist = assert_list_of_type(objlist, objtype)

        if propname in self._config and thelist is None:
            del self._config[propname]
        else:
            if thelist is not None:
                self._config[propname] = thelist

        return self

    def _remove_from_object_list(self, objlist, obj, objtype):
        """
        Removes a value from the list.

        The `obj` and any objects in the `objlist`
        must be instances of that type. The `objlist` may be None.

        If `obj` is currently a member of the list, it is removed.

        The resulting list is returned. If the resulting list is empty,
        None is returned.

        :param: objlist: A list of objects, possibly None
        :param: obj: An object
        :param: objtype: The required type of the objects and the list
        :return: The updated list.
        """
        validate_type(obj,objtype)

        newlist = []
        if objlist is not None:
            validate_list_of_type(objlist, objtype)
            for item in objlist:
                if item is not obj:
                    newlist.append(item)

        if newlist:
            return newlist
        else:
            return None

    def _remove_from_atomic_list(self, atomlist, atom):
        """
        Removes a value from the list.

        If `atom` is currently a member of the list, it is removed.

        The resulting list is returned. If the resulting list is empty,
        None is returned.

        :param: atomlist: A list of atomic values, possibly None.
        :param: atom: An atomic value
        :return: The updated list.
        """
        newlist = []
        if atomlist is not None:
            for item in atomlist:
                if item != atom:
                    newlist.append(item)

        if newlist:
            return newlist
        else:
            return None

    def remove_from_property_list(self, propname, theitem, thetype=None):
        """
        Removes an item from a configuration property list.

        The `propname` is the name of a property list.

        If `thetype` is not specified, the the list is assumed to be of
        atomic values. Otherwise, `theitem` must be instance of
        `thetype`.

        If `theitem` is currently a member of the list, it is removed from
        the list. If it is not already a member, the list returned will
        have the same members as the original list.

        Atomic values are considered equal if they compare `==`. Objects
        are considered equal if they are the same object.

        :param: propname: The name of a configuration property list
        :param: theitem: An object
        :param: thetype: The required type of the objects and the list or None
        :return: The calling object
        """
        if propname in self._config:
            thelist = self._config[propname]
            if thetype is not None:
                thelist = self._remove_from_object_list(thelist, theitem, thetype)
            else:
                thelist = self._remove_from_atomic_list(thelist, theitem)
            if thelist:
                self._config[propname] = thelist
            else:
                del self._config[propname]
