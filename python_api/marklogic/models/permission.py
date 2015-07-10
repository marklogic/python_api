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
# Norman Walsh      05/06/2015     Initial development
#

"""
Classes for manipulating MarkLogic permissions.
"""

from __future__ import unicode_literals, print_function, absolute_import

import requests
from marklogic.models.utilities.validators import *
from marklogic.models.utilities import exceptions
import json

class Permission(object):
    """
    The Permission class encapsulates a MarkLogic permission.
    A permission is the combination of a role and a capability.
    Permissions are immutable.
    """
    def __init__(self, role, capability):
        validate_capability(capability)
        self._config = {
            'role-name': role,
            'capability': capability
            }

    def role_name(self):
        """
        Return the name of the role.

        :return: The role name
        """
        return self._config['role-name']

    def capability(self):
        """
        Return the capability.

        :return: The capability.
        """
        return self._config['capability']
