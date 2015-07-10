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
# Norman Walsh      05/08/2015     Initial development

"""
Classes for dealing with path namespaces
"""

class PathNamespace:
    """
    A database path namespace.
    """
    def __init__(self, prefix, namespace_uri):
        """
        Create a path namespace.

        :param prefix: The prefix to use in field (i.e. 'foo')
        :param namespace: The namespace uri (i.e. 'http://bar.com')
        """
        self._config = {
            'prefix': prefix,
            'namespace-uri': namespace_uri
            }

    def prefix(self):
        """
        The prefix.
        """
        return self._config['prefix']

    def set_prefix(self, prefix):
        """
        Set the prefix.
        """
        self._config['prefix'] = prefix
        return self

    def namespace_uri(self):
        """
        The namespace URI.
        """
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        """
        Set the namespace URI.
        """
        self._config['namespace-uri'] = namespace_uri
        return self
