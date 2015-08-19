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
# Norman Walsh      30 July 2015     Initial development
#

from abc import ABCMeta, abstractmethod
import inspect, json, logging, re, sys

class Manager:
    """
    The base type for managers.

    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def _special_property(self, name, value):
        print("Unsupported property: {0}={1}".format(name,value))
        sys.exit(1)

    def _properties(self, obj, args):
        methods = inspect.getmembers(obj, predicate=inspect.ismethod)
        jumptable = {}
        for (name, func) in methods:
            if name.startswith('set_'):
                jumptable[name] = func

        if 'properties' in args:
            for prop in args['properties']:
                try:
                    name, value = re.split("=", prop)
                except ValueError:
                    print ("Additional properties must be name=value pairs: {0}"
                           .format(prop))
                    sys.exit(1)

                key = "set_" + name.replace("-","_")
                if key in jumptable:
                    jumptable[key](value)
                else:
                    self._special_property(name, value)

    def jprint(self, obj):
        if isinstance(obj, dict) or isinstance(obj, list):
            print(json.dumps(obj, sort_keys=True, indent=2))
        else:
            print(json.dumps(obj.marshal(), sort_keys=True, indent=2))
