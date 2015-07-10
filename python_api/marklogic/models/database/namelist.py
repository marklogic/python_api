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
Classes for dealing with lists of names, a namespace plus a list of localnames.
"""

from marklogic.models.utilities.utilities import PropertyLists

class NameList(PropertyLists):
    """
    A database name list.
    """
    def __init__(self, namespace_uri, localnames):
        """
        Create a name list.

        :param namespace_uri: The namespace uri (i.e. 'http://bar.com')
        :param localnames: A (list) of localname(s)
        """
        names = []
        if isinstance(localnames, str):
            names = [localnames]
        else:
            if type(localnames) is not list:
                raise ValidationError("List of names", repr(localnames))
            for name in localnames:
                if not(isinstance(name, str)):
                    raise ValidationError("List of names.", repr(localnames))
            names = localnames

        self._config = {
            'namespace-uri': namespace_uri,
            'localname': names
            }

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
