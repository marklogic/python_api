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
# Norman Walsh      05/10/2015     Initial development

"""
Classes for dealing with modules
"""

class ModuleLocation:
    """
    A server module location.
    """
    def __init__(self, namespace_uri, location):
        """
        Create a module mapping.

        :param namespace_uri: the namespace of the module
        :param location: the location of the module
        """
        self._config = {
            'namespace-uri': namespace_uri,
            'location': location
            }

    def namespace_uri(self):
        """
        The module namespace URI.
        """
        if self._config['namespace-uri'] == '':
            return None
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        """
        Set the module namespace URI.
        """
        self._config['namespace-uri'] = namespace_uri
        return self

    def module_location(self):
        """
        The module location.
        """
        return self._config['location']

    def set_module_location(self, location):
        """
        Set the module location.
        """
        self._config['location'] = location
        return self

