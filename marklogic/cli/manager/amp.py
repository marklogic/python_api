# -*- coding: utf-8 -*-
#
# Copyright 2015, 2016 MarkLogic Corporation
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
# Norman Walsh      24 Mar 2016   Initial development
#

"""
A class to manage amps.
"""

import json, re, sys
from marklogic.cli.manager import Manager
from marklogic.models.amp import Amp

class AmpManager(Manager):
    """
    The TaskManager performs operations on tasks.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        names = Amp.list(connection)
        print(json.dumps(names,sort_keys=True, indent=2))

    def create(self, args, config, connection):
        if args['json'] is not None:
            amp = self._read(args['json'])
        else:
            amp = Amp()

        self._handle_args(amp, args)
        self._handle_properties(amp, args)

        if amp.exists(connection=connection):
            print("Error: Amp already exists: {0}".format(amp.local_name()))
            sys.exit(1)

        amp.create(connection=connection)
        print("Created amp {}".format(amp.local_name()))

    def modify(self, args, config, connection):
        if args['json'] is not None:
            amp = self._read(args['json'])
        else:
            amp = Amp()

        self._handle_args(amp, args)
        self._handle_properties(amp, args)
        amp.update(connection=connection)

    def delete(self, args, config, connection):
        amp = Amp()

        self._handle_args(amp, args)
        self._handle_properties(amp, args)
        amp.delete(connection=connection)

    def get(self, args, config, connection):
        amp = Amp()

        self._handle_args(amp, args)
        self._handle_properties(amp, args)

        if not amp.exists(connection=connection):
            print("Error: Amp does not exist: {0}".format(args['name']))
            sys.exit(1)

        amp.read(connection=connection)
        self.jprint(amp)

    def _handle_args(self, amp, args):
        for key in args:
            value = args[key]
            if value is not None:
                if key == "name":
                    amp.set_local_name(value)
                if key == "namespace":
                    amp.set_namespace(value)
                if key == "document":
                    amp.set_document_uri(value)
                if key == "modules":
                    amp.set_modules_database(value)

    def _handle_properties(self, amp, args):
        # Handled specially because of the weird overlap between options and properties
        seen_role = False
        if 'properties' in args:
            for prop in args['properties']:
                try:
                    name, value = re.split("=", prop)
                except ValueError:
                    print ("Additional properties must be name=value pairs: {0}"
                           .format(prop))
                    sys.exit(1)

                if name == "local-name":
                    if args['name'] is not None:
                        self._duparg('name')
                    amp.set_local_name(value)
                elif name == "namespace":
                    if args['namespace'] is not None:
                        self._duparg('namespace')
                    amp.set_namespace(value)
                elif name == "document-uri":
                    if args['document'] is not None:
                        self._duparg('document')
                    amp.set_document_uri(value)
                elif name == "modules-database":
                    if args['modules'] is not None:
                        self._duparg('modules')
                    amp.set_modules_database(value)
                elif name == "role":
                    if seen_role:
                        amp.add_role_name(value)
                    else:
                        amp.set_role_names([value])
                        seen_role = True
                else:
                    print ("Unknown amp property: {0}".format(name))
                    sys.exit(1)

    def _duparg(self, name):
        print ("Cannot set '{0}' property when set as an option".format(name))
        sys.exit(1)

    def _read(self, jsonfile):
        jf = open(jsonfile).read()
        data = json.loads(jf)
        amp = Amp.unmarshal(data)
        return amp
