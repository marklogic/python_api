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
# Norman Walsh      05/07/2015     Initial development

"""
Classes for dealing with database fragment parents and roots.
"""

from __future__ import unicode_literals, print_function, absolute_import

import sys
import requests
import json
from marklogic.models.utilities.validators import *
from marklogic.models.utilities.exceptions import *

class FragmentRoot:
    """
    Fragment root.
    """
    def __init__(self, namespace_uri, localname):
        """
        Initialize a fragment root.

        :param namespace: The namespace of the fragment root element
        :param localname: The local name of the fragment root element

        :return: The fragment root object
        """

        if namespace_uri is None:
            namespace_uri = ""

        self._config = {
            'namespace-uri': namespace_uri,
            'localname': localname
            }

    def namespace_uri(self):
        if self._config['namespace-uri'] == '':
            return None
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        self._config['namespace-uri'] = namespace_uri
        return self

    def localname(self):
        return self._config['localname']

    def set_localname(self, localname):
        self._config['localname'] = localname
        return self

class FragmentParent:
    """
    Fragment parent.
    """
    def __init__(self, namespace_uri, localname):
        """
        Initialize a fragment parent.

        :param namespace: The namespace of the fragment root element
        :param localname: The local name of the fragment root element

        :return: The fragment root object
        """

        if namespace_uri is None:
            namespace_uri = ""

        self._config = {
            'namespace-uri': namespace_uri,
            'localname': localname
            }

    def namespace_uri(self):
        if self._config['namespace-uri'] == '':
            return None
        return self._config['namespace-uri']

    def set_namespace_uri(self, namespace_uri):
        self._config['namespace-uri'] = namespace_uri
        return self

    def localname(self):
        return self._config['localname']

    def set_localname(self, localname):
        self._config['localname'] = localname
        return self
