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
Classes for dealing with rulesets.
"""

class RuleSet:
    """
    A database rule set.
    """
    def __init__(self, location):
        """
        Create a rule set.

        :param location: the ruleset location
        """
        self._config = {
            'location': location
            }

    def location(self):
        """
        The location.
        """
        return self._config['location']

    def set_location(self, location):
        """
        Set the location.
        """
        self._config['location'] = location
        return self

