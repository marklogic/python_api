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

import json, logging
from abc import ABCMeta, abstractmethod
from marklogic.models.model import Model
from marklogic.models.database.ctsref import BaseReference, ElementReference
from marklogic.models.database.ctsref import ElementAttributeReference
from marklogic.models.database.ctsref import FieldReference, PathReference
from marklogic.models.database.ctsref import CollectionReference
from marklogic.exceptions import UnsupportedOperation

"""
Classes for dealing with assignment policies.
"""

class AssignmentPolicy(Model):
    """
    Defines an assignment policy.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def policy_name(self):
        return self._get_config_property('assignment-policy-name')

    def marshal(self):
        struct = {}
        for key in self._config:
            if isinstance(self._config[key], BaseReference):
                struct[key] = self._config[key].marshal()
            else:
                struct[key] = self._config[key]
        return struct

class BucketAssignmentPolicy(AssignmentPolicy):
    """
    The bucket assignment policy.
    """
    def __init__(self):
        """
        Create a bucket assignment policy.
        """
        self._config = {
            'assignment-policy-name': 'bucket'
            }

class LegacyAssignmentPolicy(AssignmentPolicy):
    """
    The legacy assignment policy.
    """
    def __init__(self):
        """
        Create a legacy assignment policy.
        """
        self._config = {
            'assignment-policy-name': 'legacy'
            }

class StatisticalAssignmentPolicy(AssignmentPolicy):
    """
    The statistical assignment policy.
    """
    def __init__(self):
        """
        Create a statistical assignment policy.
        """
        self._config = {
            'assignment-policy-name': 'statistical'
            }

class RangeAssignmentPolicy(AssignmentPolicy):
    """
    The range assignment policy.
    """
    def __init__(self, partition_key, lower_bound_included=True):
        """
        Create a range assignment policy.
        """
        self._config = {
            'assignment-policy-name': 'range',
            'lower-bound-included': lower_bound_included,
            'partition-key': partition_key
            }

    def lower_bound_included(self):
        return self._get_config_property('lower-bound-included')

    def set_lower_bound_included(self, value):
        return self._set_config_property('lower-bound-included', value)

    def partition_key(self):
        return self._get_config_property('partition-key')

    def set_partition_key(self, value):
        return self._set_config_property('partition-key', value)

    def marshal(self):
        struct = {}
        for key in self._config:
            if isinstance(self._config[key], BaseReference):
                struct[key] = self._config[key].marshal()
            elif isinstance(self._config[key], PartitionKey):
                struct[key] = self._config[key].marshal()
            else:
                struct[key] = self._config[key]
        return struct

    @classmethod
    def unmarshal(cls, config):
        logger = logging.getLogger("marklogic")
        key = config['partition-key']
        if 'element-reference' in key:
            keytype = 'element-reference'
        elif 'element-attribute-reference' in key:
            keytype = 'element-attribute-reference'
        elif 'field-reference' in key:
            keytype = 'field-reference'
        elif 'path-reference' in key:
            keytype = 'path-reference'
        elif 'collection-reference' in key:
            keytype = 'collection-reference'
        else:
            raise UnsupportedOperation("Unexpected partition key type: "
                                       + json.dumps(config['partition-key']))

        key = key[keytype]

        collation = None
        coordsys = None
        nullable = None

        if key is not None:
            if 'collation' in key:
                collation = key['collation']
            if 'coordinate-system' in key:
                coordsys = key['coordinate-system']
            if 'nullable' in key:
                nullable = key['nullable']

        if keytype == 'element-reference':
            pkey = ElementReference(key['namespace-uri'],
                                    key['localname'],
                                    key['scalar-type'],
                                    collation, coordsys, nullable)
        elif keytype == 'element-attribute-reference':
            pkey = ElementAttributeReference(key['parent-namespace-uri'],
                                             key['parent-localname'],
                                             key['namespace-uri'],
                                             key['localname'],
                                             key['scalar-type'],
                                             collation, coordsys, nullable)
        elif keytype == 'field-reference':
            pkey = FieldReference(key['field-name'],
                                  key['scalar-type'],
                                  collation, coordsys, nullable)
        elif keytype == 'path-reference':
            pkey = PathReference(key['path-expression'],
                                 key['scalar-type'],
                                 collation, coordsys, nullable)
        elif keytype == 'collection-reference':
            pkey = CollectionReference(nullable)
        else:
            raise UnsupportedOperation("Unexpected partition key type: "
                                       + json.dumps(config['partition-key']))

        return RangeAssignmentPolicy(pkey, config['lower-bound-included'])

class PartitionKey(Model):
    """
    The partition key for range assignment policies.
    """
    def __init__(self, cts_reference):
        """
        Create a partition key with a given reference.
        """
        if isinstance(cts_reference, ElementReference):
            self._config = {
                'element-reference': cts_reference
                }
        else:
            raise UnsupportedOperation("Only element references are supported")

    def reference(self):
        return self._get_config_property('element-reference')

    def set_reference(self, cts_reference):
        if isinstance(cts_reference, ElementReference):
            self._set_config_property('element-reference', cts_reference)
        else:
            raise UnsupportedOperation("Only element references are supported")

    def marshal(self):
        if 'element-reference' in self._config:
            er = self._config['element-reference']
            struct = er.marshal()
        else:
            struct = {'x':'y'}
        return struct

    @classmethod
    def unmarshal(cls, config):
        logger = logging.getLogger("marklogic")
        logger.info(config)
