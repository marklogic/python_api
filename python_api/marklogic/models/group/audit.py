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
# Norman Walsh      08/09/2015     Initial development

"""
Classes for dealing with group auditing
"""

from __future__ import unicode_literals, print_function, absolute_import
from marklogic.models.model import Model

class Audit(Model):
    def __init__(self, enabled, keep_files=7, rotate="daily",
                 events=None, restrictions=None):
        """
        Create an audit.
        """
        self._config = {
            'audit-enabled': enabled,
            'keep-audit-files': keep_files,
            'rotate-audit-files': rotate
        }

        if events is not None:
            self._config['audit-event'] = events
        if restrictions is not None:
            self._config['audit-restriction'] = restrictions

class AuditEvent(Model):
    def __init__(self, name, enabled):
        self._config = {
            'audit-event-name': name,
            'audit-event-enabled': enabled
        }

class AuditRestriction(Model):
    def __init__(self, name, atype, items):
        self._config = {
            'audit-restriction-name': name,
            'audit-restriction-type': atype,
            'audit-restriction-items': items
        }
