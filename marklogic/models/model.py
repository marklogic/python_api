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
# Norman Walsh      19 July 2015     Initial development
#

from abc import ABCMeta
from marklogic.utilities.validators import ValidationError
from marklogic.exceptions import UnsupportedOperation


class Model:
    """
    The base type for models. Defines a few general methods.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def _get_config_property(self, key):
        if key in self._config:
            return self._config[key]
        else:
            return None

    def _set_config_property(self, key, value):
        self._config[key] = value
        return self

    def _validate(self, value, vtype):
        if isinstance(vtype, list):
            if value not in vtype:
                raise ValidationError("Not in list: {0}"
                                      .format(", ".join(vtype)),
                                      value)
        elif isinstance(vtype, dict):
            try:
                value = int(value)
            except ValueError:
                raise ValidationError("Not an integer", value)
            if 'min' in vtype and value < vtype['min']:
                raise ValidationError("Value too small (min={0})"
                                      .format(vtype['min']), value)
            if 'max' in vtype and value > vtype['max']:
                raise ValidationError("Value too large (max={0})"
                                      .format(vtype['max']), value)
        elif vtype == 'boolean':
            if not isinstance(value, bool):
                raise ValidationError("Not a boolean", value)
        elif vtype == 'integer':
            try:
                value = int(value)
            except ValueError:
                raise ValidationError("Not an integer", value)
            if value != 'true' and value != 'false':
                raise ValidationError("Not a boolean", value)
        elif vtype == 'string':
            pass
        else:
            raise UnsupportedOperation("Unexpected type: {0}"
                                       .format(vtype))
