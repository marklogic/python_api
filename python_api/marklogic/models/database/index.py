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
# Paul Hoehne       03/01/2015     Initial development
# Norman Walsh      05/07/2015     Hacked in more index types
#

from abc import ABCMeta, abstractmethod
from marklogic.models.utilities.validators import validate_index_type
from marklogic.models.utilities.validators import validate_index_invalid_value_actions
from marklogic.models.utilities.validators import validate_boolean
from marklogic.models.utilities.validators import validate_collation

class _Index:
    """
    Defines a MarkLogic index.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def range_value_positions(self):
        """
        Returns range value positions.

        :return: The range value positions setting
        """
        if 'range-value-positions' in self._config:
            return self._config['range-value-positions']
        return None

    def set_range_value_positions(self, pos=False):
        """
        Sets the range value positions.

        :param pos: The range value positions setting

        :return: The index object
        """
        validate_boolean(pos)
        self._config['range-value-positions'] = pos
        return self

    def invalid_values(self):
        """
        Returns invalid values setting.

        :return: The invalid values setting
        """
        if 'invalid-values' in self._config:
            return self._config['invalid-values']
        return None

    def set_invalid_values(self, invalid='reject'):
        """
        Sets the invalid values setting.

        :param invalid: The invalid values setting

        :return: The index object
        """
        validate_index_invalid_value_actions(invalid)
        self._config['invalid-values'] = invalid
        return self

class _RangeIndex(_Index):
    """
    Defines a MarkLogic range index.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def scalar_type(self):
        """
        Returns scalar type of the index.

        :return: The scalar type of the index.
        """
        if 'scalar-type' in self._config:
            return self._config['scalar-type']
        return None

    def set_scalar_type(self, scalar='string'):
        """
        Sets the index type

        :param scalar: The scalar type of the index

        :return: The index object
        """
        # FIXME: validate_scalar_type(scalar)
        self._config['scalar-type'] = scalar
        return self

    def collation(self):
        """
        Returns the collation. Collations are only relevant to string
        indexes. ``None`` is returned for all non-string indexes.

        :return: The collation URI.
        """
        if self.scalar_type() != 'string':
            return None

        if 'collation' in self._config:
            return self._config['collation']

        return None

    def set_collation(self, collation):
        """
        Sets the collation

        :param collation: The collation URI.

        :return: The index object
        """
        # FIXME: validate_collation(collation)
        self._config['collation'] = collation
        return self

class _LocalNameIndex():
    """
    A mixin for indexes that have local names.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def namespace_uri(self):
        """
        Returns the namespace-uri.

        :return: The namespace-uri URI.
        """
        if 'namespace-uri' in self._config:
            return self._config['namespace-uri']
        return None

    def set_namespace_uri(self, namespace_uri):
        """
        Sets the namespace URI

        :param namespace_uri: The namespace URI.

        :return: The index object
        """
        # FIXME: validate_namespace-uri(namespace_uri)
        self._config['namespace-uri'] = namespace_uri
        return self

    def localname(self):
        """
        Returns the localname.

        :return: The localname URI.
        """
        if 'localname' in self._config:
            return self._config['localname']
        return None

    def set_localname(self, localname):
        """
        Sets the localname

        :param localname: The localname URI.

        :return: The index object
        """
        # FIXME: validate_localname(localname)
        self._config['localname'] = localname
        return self

class _ParentNameIndex():
    """
    A mixin for indexes that have parent names.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def parent_namespace_uri(self):
        """
        Returns the parent namespace URI.

        :return: The parent namespace URI.
        """
        if 'parent-namespace-uri' in self._config:
            return self._config['parent-namespace-uri']
        return None

    def set_parent_namespace_uri(self, parent_namespace_uri):
        """
        Sets the parent namespace URI

        :param parent_namespace_uri: The parent namespace URI.

        :return: The index object
        """
        # FIXME: validate_namespace-uri(parent_namespace_uri)
        self._config['parent-namespace-uri'] = parent_namespace_uri
        return self

    def parent_localname(self):
        """
        Returns the parent localname.

        :return: The parent localname URI.
        """
        if 'parent-localname' in self._config:
            return self._config['parent-localname']
        return None

    def set_parent_localname(self, parent_localname):
        """
        Sets the parent localname

        :param parent_localname: The parent localname.

        :return: The index object
        """
        # FIXME: validate_localname(parent_localname)
        self._config['parent-localname'] = parent_localname
        return self

class ElementRangeIndex(_RangeIndex, _LocalNameIndex):
    """
    An element range index.
    """
    def __init__(self, scalar_type, namespace_uri, localname,
                 collation="", range_value_positions=False,
                 invalid_values='reject'):
        """
        Create an element range index.
        """
        validate_index_type(scalar_type)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)
        validate_collation(scalar_type, collation)

        if collation == '':
            collation = None

        self._config = {
            'scalar-type': scalar_type,
            'namespace-uri': namespace_uri,
            'localname': localname,
            'collation': '',
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

        if collation is not None:
            self._config['collation'] = collation

class AttributeRangeIndex(_RangeIndex, _LocalNameIndex, _ParentNameIndex):
    """
    An attribute range index.
    """
    def __init__(self, scalar_type,
                 parent_uri, parent_localname,
                 namespace_uri, localname,
                 collation="", range_value_positions=False,
                 invalid_values='reject'):
        """
        Create an attribute range index.
        """
        validate_index_type(scalar_type)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)
        validate_collation(scalar_type, collation)

        if collation == '':
            collation = None

        self._config = {
            'scalar-type': scalar_type,
            'parent-namespace-uri': parent_uri,
            'parent-localname': parent_localname,
            'namespace-uri': namespace_uri,
            'localname': localname,
            'collation': '',
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

        if collation is not None:
            self._config['collation'] = collation

class _PathExpressionIndex():
    """
    A mixin for indexes that have path expressions.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def path_expression(self):
        """
        Returns the path expression,
        the path to the root of the field.

        :return: The path expression.
        """
        if 'path-expression' in self._config:
            return self._config['path-expression']
        return None

    def set_path_expression(self, path_expression):
        """
        Sets the path expression.

        :param path_expression: The path expression.

        :return: The index object
        """
        # FIXME: validate_path_expression(path_expression)
        self._config['path-expression'] = path_expression
        return self

class PathRangeIndex(_RangeIndex, _PathExpressionIndex):
    """
    A path range index.
    """
    def __init__(self, scalar_type, path_expr,
                 collation="", range_value_positions=False,
                 invalid_values='reject'):
        """
        Create a path range index.
        """
        validate_index_type(scalar_type)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)
        validate_collation(scalar_type, collation)

        if collation == '':
            collation = None

        self._config = {
            'scalar-type': scalar_type,
            'path-expression': path_expr,
            'collation': '',
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

        if collation is not None:
            self._config['collation'] = collation

class FieldRangeIndex(_RangeIndex):
    """
    A field range index.
    """
    def __init__(self, scalar_type, field_name,
                 collation="", range_value_positions=False,
                 invalid_values='reject'):
        """
        Create a field range index.
        """
        validate_index_type(scalar_type)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)
        validate_collation(scalar_type, collation)

        if collation == '':
            collation = None

        self._config = {
            'scalar-type': scalar_type,
            'field-name': field_name,
            'collation': '',
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

        if collation is not None:
            self._config['collation'] = collation

    def field_name(self):
        """
        Returns the field name.

        :return: The field name.
        """
        if 'field-name' in self._config:
            return self._config['field-name']
        return None

    def set_field_name(self, field_name):
        """
        Sets the field name.

        :param field_name: The field name.

        :return: The index object
        """
        # FIXME: validate_field_name(field_name)
        self._config['field-name'] = field_name
        return self

class _GeospatialIndex(_Index):
    """
    Defines a MarkLogic geospatal index.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def coordinate_system(self):
        """
        Returns the coordinate system used for points in the index.

        :return: The coordinate system.
        """
        if 'coordinate-system' in self._config:
            return self._config['coordinate-system']
        return None

    def set_coordinate_system(self, coordinate_system):
        """
        Sets the coordinate system used for points in the index.

        :param coordinate_system: The coordinate system.

        :return: The index object
        """
        # FIXME: validate_coordinate_system(coordinate_system)
        self._config['coordinate-system'] = coordinate_system
        return self

    def point_format(self):
        """
        Returns the point format used for points in the index.

        :return: The point format.
        """
        if 'point-format' in self._config:
            return self._config['point-format']
        return None

    def set_point_format(self, point_format):
        """
        Sets the point format used for points in the index.

        :param point_format: The point format.

        :return: The index object
        """
        # FIXME: validate_point_format(point_format)
        self._config['point-format'] = point_format
        return self

class GeospatialElementIndex(_GeospatialIndex, _ParentNameIndex):
    """
    A geospatial element index.
    """
    def __init__(self, namespace_uri, localname,
                 coordinate_system="wgs84", point_format="point",
                 range_value_positions=False, invalid_values='reject'):
        """
        Create a geospatial element index.
        """
        validate_coordinate_system(coordinate_system)
        validate_point_format(point_format)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)

        self._config = {
            'namespace-uri': namespace_uri,
            'localname': localname,
            'coordinate-system': coordinate_system,
            'point-format': point_format,
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

class GeospatialPathIndex(_GeospatialIndex, _PathExpressionIndex):
    """
    A geospatial path index.
    """
    def __init__(self, path_expr,
                 coordinate_system="wgs84", point_format="point",
                 range_value_positions=False, invalid_values='reject'):
        """
        Create a geospatial path index.
        """
        validate_coordinate_system(coordinate_system)
        validate_point_format(point_format)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)

        self._config = {
            'path-expression': path_expr,
            'coordinate-system': coordinate_system,
            'point-format': point_format,
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

class GeospatialElementChildIndex(GeospatialElementIndex, _ParentNameIndex):
    """
    A geospatial element index.
    """
    def __init__(self, parent_uri, parent_localname, namespace_uri, localname,
                 coordinate_system="wgs84", point_format="point",
                 range_value_positions=False, invalid_values='reject'):
        """
        Create a geospatial element index.
        """
        validate_coordinate_system(coordinate_system)
        validate_point_format(point_format)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)

        self._config = {
            'parent-namespace-uri': parent_uri,
            'parent-localname': parent_localname,
            'namespace-uri': namespace_uri,
            'localname': localname,
            'coordinate-system': coordinate_system,
            'point-format': point_format,
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

class GeospatialElementPairIndex(_GeospatialIndex, _ParentNameIndex):
    """
    A geospatial element pair index.
    """
    def __init__(self, parent_uri, parent_localname,
                 long_namespace_uri, long_localname,
                 lat_namespace_uri, lat_localname,
                 coordinate_system="wgs84",
                 range_value_positions=False, invalid_values='reject'):
        """
        Create a geospatial element pair index.
        """
        validate_coordinate_system(coordinate_system)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)

        self._config = {
            'parent-namespace-uri': parent_uri,
            'parent-localname': parent_localname,
            'longitude-namespace-uri': long_namespace_uri,
            'longitude-localname': long_localname,
            'latitude-namespace-uri': lat_namespace_uri,
            'latitude-localname': lat_localname,
            'coordinate-system': coordinate_system,
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }

    def longitude_namespace_uri(self):
        """
        Returns the longitude namespace URI.

        :return: The longitude namespace URI.
        """
        if 'longitude-namespace-uri' in self._config:
            return self._config['longitude-namespace-uri']
        return None

    def set_longitude_namespace_uri(self, longitude_namespace_uri):
        """
        Sets the longitude namespace URI

        :param longitude_namespace_uri: The longitude namespace URI.

        :return: The index object
        """
        # FIXME: validate_namespace_uri(longitude_namespace_uri)
        self._config['longitude-namespace-uri'] = longitude_namespace_uri
        return self

    def longitude_localname(self):
        """
        Returns the longitude localname.

        :return: The longitude localname URI.
        """
        if 'longitude-localname' in self._config:
            return self._config['longitude-localname']
        return None

    def set_longitude_localname(self, longitude_localname):
        """
        Sets the longitude localname

        :param longitude_localname: The longitude localname.

        :return: The index object
        """
        # FIXME: validate_localname(longitude_localname)
        self._config['longitude-localname'] = longitude_localname
        return self

    def latitude_namespace_uri(self):
        """
        Returns the latitude namespace URI.

        :return: The latitude namespace URI.
        """
        if 'latitude-namespace-uri' in self._config:
            return self._config['latitude-namespace-uri']
        return None

    def set_latitude_namespace_uri(self, latitude_namespace_uri):
        """
        Sets the latitude namespace URI

        :param latitude_namespace_uri: The latitude namespace URI.

        :return: The index object
        """
        # FIXME: validate_namespace_uri(latitude_namespace_uri)
        self._config['latitude-namespace-uri'] = latitude_namespace_uri
        return self

    def latitude_localname(self):
        """
        Returns the latitude localname.

        :return: The latitude localname URI.
        """
        if 'latitude-localname' in self._config:
            return self._config['latitude-localname']
        return None

    def set_latitude_localname(self, latitude_localname):
        """
        Sets the latitude localname

        :param latitude_localname: The latitude localname.

        :return: The index object
        """
        # FIXME: validate_localname(latitude_localname)
        self._config['latitude-localname'] = latitude_localname
        return self

class GeospatialElementAttributePairIndex(GeospatialElementPairIndex):
    """
    A geospatial element attribute pair index.
    """
    def __init__(self, parent_uri, parent_localname,
                 long_namespace_uri, long_localname,
                 lat_namespace_uri, lat_localname,
                 coordinate_system="wgs84",
                 range_value_positions=False, invalid_values='reject'):
        """
        Create a geospatial element attribute pair index.
        """
        validate_coordinate_system(coordinate_system)
        validate_boolean(range_value_positions)
        validate_index_invalid_value_actions(invalid_values)

        self._config = {
            'parent-namespace-uri': parent_uri,
            'parent-localname': parent_localname,
            'longitude-namespace-uri': long_namespace_uri,
            'longitude-localname': long_localname,
            'latitude-namespace-uri': lat_namespace_uri,
            'latitude-localname': lat_localname,
            'coordinate-system': coordinate_system,
            'range-value-positions': range_value_positions,
            'invalid-values': invalid_values
        }
