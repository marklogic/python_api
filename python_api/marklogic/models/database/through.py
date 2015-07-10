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
Classes for dealing with phrase arounds, phrase throughs, and query throughs.
"""

from marklogic.models.utilities.validators import assert_list_of_type
from marklogic.models.utilities.utilities import PropertyLists

class _Through(PropertyLists):
    """
    A phrase through or around.
    """
    def __init__(self):
        raise ValueError("Do not instantiate _Through directly")

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

    def localnames(self):
        """
        The localnames.
        """
        if 'localname' in self._config['localname']:
            return self._config['localname']
        else:
            return None

    def add_localname(self, name):
        """
        Add a localname.
        """
        return self.add_to_property_list('localname', name)

    def remove_localname(self, name):
        """
        Remove a localname.
        """
        return self.remove_from_property_list('localname', name)

    def set_localnames(self, names):
        """
        Set the list of localnames.
        """
        return self.set_property_list('localname', names)

class PhraseThrough(_Through):
    """
    A phrase through.
    """
    def __init__(self, namespace_uri, localnames):
        """
        Create a phrase through.
        """
        self._config = {
            'namespace-uri': namespace_uri,
            'localname': assert_list_of_type(localnames, str)
            }

class PhraseAround(_Through):
    """
    A phrase around.
    """
    def __init__(self, namespace_uri, localnames):
        """
        Create a phrase around.
        """
        self._config = {
            'namespace-uri': namespace_uri,
            'localname': assert_list_of_type(localnames, str)
            }

class ElementWordQueryThrough(_Through):
    """
    An element word query through.
    """
    def __init__(self, namespace_uri, localnames):
        """
        Create an element word query through.
        """
        self._config = {
            'namespace-uri': namespace_uri,
            'localname': assert_list_of_type(localnames, str)
            }
