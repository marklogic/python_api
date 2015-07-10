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
# Paul Hoehne       03/05/2015     Initial development
#


"""
Validators are utility functions used by various classes to validate
input.
"""

class ValidationError(Exception):
    """
    A validation error class
    """
    def __init__(self, message, original_value):
        self._message = message
        self._original_value = original_value

    def __repr__(self):
        "Validation Error('{0}', {1})".format(self._message, self._original_value)


def validate_boolean(raw_val):
    """
    Validate a boolean.
    """
    if type(raw_val) != bool:
        raise ValidationError('Value passed is not a boolean', repr(raw_val))


def validate_index_type(raw_val):
    """
    Validate a scalar index type.
    """
    valid_index_types = {"int", "unsignedInt", "long", "unsignedLong", "float", "double", "decimal", "dateTime",
                         "time", "date",  "gYearMonth", "gYear", "gMonth", "gDay", "yearMonthDuration",
                         "dayTimeDuration", "string", "anyURI"}
    if raw_val not in valid_index_types:
        raise ValidationError('Value is not a valid index type', repr(raw_val))


def validate_index_invalid_value_actions(raw_val):
    """
    Validate the invalid value actions on an index.
    """
    valid_actions = {'ignore', 'reject'}

    if raw_val not in valid_actions:
        raise ValidationError("Value is not a valid action for invalid index values", repr(raw_val))


def validate_stemmed_searches_type(raw_val):
    """
    Validate the stemmed searches value.
    """
    valid_types = {'off', 'basic', 'advanced', 'decompounding'}

    if raw_val not in valid_types:
        raise ValidationError("Stemmed search type is not a valid type of stemmed search", repr(raw_val))


def validate_integer_range(raw_val, min, max):
    """
    Validate an intenger in a range.
    """
    if raw_val not in range(min, (1 + max)):
        raise ValidationError("Integer value out of range", repr(raw_val))


def validate_directory_creation(raw_val):
    """
    Validate the directory creation setting.
    """
    if raw_val not in ['manual', 'automatic', 'manual-enforced']:
        raise ValidationError("Invalid directory creation method", repr(raw_val))


def validate_locking_type(raw_val):
    """
    Validate locking type.
    """
    if raw_val not in ['strict', 'fast', 'off']:
        raise ValidationError("Invalid locking option", repr(raw_val))


def validate_range_index_optimize_options(raw_val):
    """
    Validate a range index optimization option.
    """
    if raw_val not in ['facet-time', 'memory-size']:
        raise ValidationError("Range index optimize option is not a valid value", repr(raw_val))


def validate_format_compatibility_options(raw_val):
    """
    Validate a format compatability option.
    """
    if raw_val not in ['5.0', '4.2', '4.1', '4.0', '3.2']:
        raise ValidationError("On disk index format comatibility objest is not a valide value", repr(raw_val))

def validate_index_detection_options(raw_val):
    """
    Validate an index detection option.
    """
    if raw_val not in ['automatic', 'none']:
        raise ValidationError("Index detection options is not a valid value", repr(raw_val))


def validate_expunge_locks_options(raw_val):
    """
    Validate an expunge locks option.
    """
    if raw_val not in ['automatic', 'none']:
        raise ValidationError("Expunge locks option is not a valid value", repr(raw_val))


def validate_term_frequency_normalization_options(raw_val):
    """
    Validate a term frequency normalization option.
    """
    if raw_val not in ['unscaled-log', 'weakest-scaled-log', 'weakly-scaled-log', 'moderately-scaled-log',
                      'strongly-scaled-log', 'scaled-log']:
        raise ValidationError("Term frequency normalization option is not a valid value", repr(raw_val))


def validate_merge_priority_options(raw_val):
    """
    Validate a merge priority optoin.
    """
    if raw_val not in ['lower', 'normal']:
        raise ValidationError("Merge priority option is not a valid value", repr(raw_val))


def validate_assignment_policy_options(raw_val):
    """
    Validate an assignment policy option.
    """
    if raw_val not in ['bucket', 'statistical', 'range', 'legacy']:
        raise ValidationError("Assignment policy option is not a valid value", repr(raw_val))

def validate_privilege_kind(raw_val):
    """
    Validate a privilege kind.
    """
    if raw_val not in ['uri', 'execute']:
        raise ValidationError("Privilege kind is not a valid value", repr(raw_val))

def validate_custom(message):
    """
    Raise a validation error.
    """
    raise ValidationError("Validation error", repr(message))


def validate_forest_availability(raw_val):
    """
    Validate a forest availability value.
    """
    if raw_val not in ['online', 'offline']:
        raise ValidationError("Forest availability status is not a valid value", repr(raw_val))

def validate_string(raw_val):
    """
    Validate that the value is a string.
    """
    if type(raw_val) is not str:
        raise ValidationError("String expected.", repr(raw_val))

def validate_list_of_strings(raw_val):
    """
    Validate that the value is a list of strings.
    """
    if type(raw_val) is not list:
        raise ValidationError("List of strings expected.", repr(raw_val))
    for value in raw_val:
        if type(value) is not str:
            raise ValidationError("List of strings expected.", repr(raw_val))

def validate_coordinate_system(raw_val):
    """
    Validate a geospatial index coordinate system.
    """
    if raw_val not in ['wgs84', 'raw']:
        raise ValidationError("Invalid coordinate system", repr(raw_val))

def validate_point_format(raw_val):
    """
    Validate a geospatial index point format.
    """
    if raw_val not in ['point', 'lat-long-point']:
        raise ValidationError("Invalid point format", repr(raw_val))

def validate_capability(raw_val):
    """
    Validate a capability.
    """
    if raw_val not in ['read', 'insert', 'update', 'execute']:
        raise ValidationError("Invalid capability", repr(raw_val))

def validate_collation(index_type, collation):
    """
    Validate a colation for an index type.
    """
    # FIXME: really validate the collation string!
    if index_type == "string":
        return
    if (index_type == "anyURI"
        and collation == "http://marklogic.com/collation/codepoint"):
        return
    if collation is None or collation == "":
        return
    raise ValidationError('Collation cannot be {0} for an index of type {1}' \
                          .format(index_type, collation))

def validate_type(raw_val, cls):
    """
    Validate that the value is of the specified type.
    """
    if not isinstance(raw_val, cls):
        raise ValidationError('Value passed is not a {0}' \
                              .format(cls.__name__), repr(raw_val))

def assert_type(raw_val, cls):
    """
    Assert that the value is of the specified type.

    :return The value if it passes the type test, otherwise raise an exception
    """
    if isinstance(raw_val, cls):
        return raw_val
    raise ValidationError('Value passed is not a {0}' \
       .format(cls.__name__), repr(raw_val))

def assert_boolean(raw_val):
    """
    Assert that the value is boolean.

    :return The value if it is boolean, otherwise raise an exception
    """
    return assert_type(raw_val, bool)

def validate_list_of_type(raw_val, cls):
    """
    Validate a list of the specified type.
    """
    if type(raw_val) is not list:
        raise ValidationError("List of {0} expected.".format(cls.__name__),
                              repr(raw_val))
    for value in raw_val:
        if type(value) is not cls:
            raise ValidationError("List of {0} expected.".format(cls.__name__),
                                  repr(raw_val))

def assert_list_of_type(raw_val, cls):
    """
    Assert that the value is a list of the specified type.

    A single value of the specified type is returned as a list of length 1.

    :return The value if it is an appropriate list, otherwise raise an exception
    """
    if type(raw_val) is cls:
        return [ raw_val ]
    validate_list_of_type(raw_val, cls)
    return raw_val

