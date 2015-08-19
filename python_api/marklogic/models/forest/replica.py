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
# Norman Walsh      17 August 2015   Initial development

"""
Classes for dealing with forest replicas
"""

import json, requests
import marklogic.utilities.validators
import marklogic.exceptions
from marklogic.models.model import Model

class ForestReplica(Model):
    """
    A forest replica.
    """
    def __init__(self, name, host, data_dir="", large_data_dir="",
                 fast_data_dir=""):
        self._config = {
            'replica-name': name,
            'host': host,
            'data-directory': data_dir,
            'large-data-directory': large_data_dir,
            'fast-data-directory': fast_data_dir
            }

