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
# Norman Walsh      08/07/2015     Initial development

from abc import ABCMeta, abstractmethod
from marklogic.models.model import Model

"""
Classes for dealing with CTS references.
"""

class BaseReference(Model):
    """
    Defines an abstract CTS base reference.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def scalar_type(self):
        return self._get_config_property('scalar-type')

    def set_scalar_type(self, value):
        return self._set_config_property('scalar-type', value)

    def collation(self):
        return self._get_config_property('collation')

    def set_collation(self, value):
        return self._set_config_property('collation', value)

    def coordinate_system(self):
        return self._get_config_property('coordinate-system')

    def set_coordinate_system(self, value):
        return self._set_config_property('coordinate-system', value)

    def nullable(self):
        return self._get_config_property('nullable')

    def set_nullable(self, value):
        return self._set_config_property('nullable', value)

    def marshal(self):
        struct = {}
        struct[self.propname] = {}
        for key in self._config:
            struct[self.propname][key] = self._config[key]
        return struct

class ElementReference(BaseReference):
    """
    An element reference.
    """
    def __init__(self, namespace_uri, localname, scalar_type,
                 collation=None, coordinate_system=None, nullable=None):
        """
        Create an element reference.
        """
        self.propname = 'element-reference'
        self._config = {
            'namespace-uri': namespace_uri,
            'localname': localname,
            'scalar-type': scalar_type
            }
        if collation is not None:
          self._config['collation'] = collation
        if coordinate_system is not None:
          self._config['coordinate-system'] = coordinate_system
        if nullable is not None:
          self._config['nullable'] = nullable

    def namespace_uri(self):
        return self._get_config_property('namespace-uri')

    def set_namespace_uri(self, value):
        return self._set_config_property('namespace-uri', value)

    def localname(self):
        return self._get_config_property('localname')

    def set_localname(self, value):
        return self._set_config_property('localname', value)

class ElementAttributeReference(BaseReference):
    """
    An element attribute reference.
    """
    def __init__(self, parent_namespace_uri, parent_localname,
                 namespace_uri, localname, scalar_type,
                 collation=None, coordinate_system=None, nullable=None):
        """
        Create an element attribute reference.
        """
        self.propname = 'element-attribute-reference'
        self._config = {
            'parent-namespace-uri': parent_namespace_uri,
            'parent-localname': parent_localname,
            'namespace-uri': namespace_uri,
            'localname': localname,
            'scalar-type': scalar_type
            }
        if collation is not None:
          self._config['collation'] = collation
        if coordinate_system is not None:
          self._config['coordinate-system'] = coordinate_system
        if nullable is not None:
          self._config['nullable'] = nullable

    def parent_namespace_uri(self):
        return self._get_config_property('parent-namespace-uri')

    def set_parent_namespace_uri(self, value):
        return self._set_config_property('parent-namespace-uri', value)

    def parent_localname(self):
        return self._get_config_property('parent-localname')

    def set_parent_localname(self, value):
        return self._set_config_property('parent-localname', value)

    def namespace_uri(self):
        return self._get_config_property('namespace-uri')

    def set_namespace_uri(self, value):
        return self._set_config_property('namespace-uri', value)

    def localname(self):
        return self._get_config_property('localname')

    def set_localname(self, value):
        return self._set_config_property('localname', value)

class FieldReference(BaseReference):
    """
    A field reference.
    """
    def __init__(self, field_name, scalar_type,
                 collation=None, coordinate_system=None, nullable=None):
        """
        Create a field reference.
        """
        self.propname = 'field-reference'
        self._config = {
            'field-name': field_name,
            'scalar-type': scalar_type
            }
        if collation is not None:
          self._config['collation'] = collation
        if coordinate_system is not None:
          self._config['coordinate-system'] = coordinate_system
        if nullable is not None:
          self._config['nullable'] = nullable

    def field_name(self):
        return self._get_config_property('field-name')

    def set_field_name(self, value):
        return self._set_config_property('field-name', value)

class PathReference(BaseReference):
    """
    A path reference.
    """
    def __init__(self, path_expr, scalar_type,
                 collation=None, coordinate_system=None, nullable=None):
        """
        Create a path reference.
        """
        self.propname = 'path-reference'
        self._config = {
            'path-expression': path_expr,
            'scalar-type': scalar_type
            }
        if collation is not None:
          self._config['collation'] = collation
        if coordinate_system is not None:
          self._config['coordinate-system'] = coordinate_system
        if nullable is not None:
          self._config['nullable'] = nullable

    def path_expression(self):
        return self._get_config_property('path-expression')

    def set_path_expression(self, value):
        return self._set_config_property('path-expression', value)

class CollectionReference(BaseReference):
    """
    A collection reference.
    """
    def __init__(self, nullable=None):
        """
        Create a collection reference.
        """
        self.propname = 'collection-reference'
        self._config = {}
        if nullable is not None:
          self._config['nullable'] = nullable

    # FIXME: Make references to type, collation, etc. errors.

    def marshal(self):
        substruct = {}
        for key in self._config:
            substruct[self.propname][key] = self._config[key]

        struct = {}
        if len(substruct) == 0:
            struct[self.propname] = None
        else:
            struct[self.propname] = substruct

        return struct

