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
Classes for dealing with namespaces
"""

class UsingNamespace:
    """
    A server namespace.
    """
    def __init__(self, namespace_uri):
        """
        Create a server namespace

        :param namespace_uri: the namespace of the namespace
        """
        self._config = {
            'namespace-uri': namespace_uri
            }

    def namespace_uri(self):
        """
        The server namespace URI.
        """
        if self._config['namespace-uri'] == '':
            return None
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        """
        Set the server namespace URI.
        """
        self._config['namespace-uri'] = namespace_uri
        return self

class Namespace(UsingNamespace):
    """
    A server namespace mapping.
    """
    def __init__(self, prefix, namespace_uri):
        """
        Create a namespace mapping.

        :param prefix: the prefix
        :param namespace_uri: the namespace of the namespace
        """
        self._config = {
            'prefix': prefix,
            'namespace-uri': namespace_uri
            }

    def prefix(self):
        """
        The server namespace prefix.
        """
        return self._config['prefix']

    def set_prefix(self, location):
        """
        Set the server namespace prefix.
        """
        self._config['prefix'] = location
        return self

