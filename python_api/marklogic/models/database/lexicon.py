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
Classes for dealing with lexicons
"""

class _Lexicon:
    """
    A lexicon. This class is abstract.
    """
    def __init__(self):
        raise ValueError("Do not instantiate _Lexicon directly")

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

    def localname(self):
        """
        The localname.
        """
        return self._config['localname']

    def set_localname(self, localname):
        """
        Set the localname.
        """
        self._config['localname'] = localname
        return self

    def collation(self):
        """
        The collation.
        """
        return self._config['collation']

    def set_collation(self, collation):
        """
        Set the collation.
        """
        self._config['collation'] = collation
        return self

class ElementWordLexicon(_Lexicon):
    """
    An elmeent word lexicon
    """
    def __init__(self, namespace_uri, localname,
                 collation="http://marklogic.com/collation/"):
        """
        Create an elmeent word lexicon
        """
        self._config = {
            'namespace-uri': namespace_uri,
            'localname': localname,
            'collation': collation
            }

class AttributeWordLexicon(_Lexicon):
    """
    An element attribute word lexicion.
    """
    def __init__(self, parent_namespace_uri, parent_localname,
                 namespace_uri, localname,
                 collation="http://marklogic.com/collation/"):
        """
        Create an element attribute word lexicion.
        """
        self._config = {
            'parent-namespace-uri': parent_namespace_uri,
            'parent-localname': parent_localname,
            'namespace-uri': namespace_uri,
            'localname': localname,
            'collation': collation
            }

    def parent_namespace_uri(self):
        return self._config['parent-namespace-uri']

    def set_parent_namespace_uri(self, namespace_uri):
        self._config['parent-namespace-uri'] = namespace_uri
        return self

    def parent_localname(self):
        return self._config['parent-localname']

    def set_parent_localname(self, localname):
        self._config['parent-localname'] = localname
        return self

