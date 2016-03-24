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
# Norman Walsh      23 Mar 2016   Initial development
#

"""
A class to manage tasks.
"""

import json, sys
from marklogic.cli.manager import Manager
from marklogic.models.task import Task

class TaskManager(Manager):
    """
    The TaskManager performs operations on tasks.
    """
    def __init__(self):
        pass

    def list(self, args, config, connection):
        names = Task.list(connection)
        print(json.dumps(names,sort_keys=True, indent=2))

    def create(self, args, config, connection):
        if args['json'] is not None:
            task = self._read(None, args['json'], args['group'])
        else:
            task = Task(connection=connection)

        task.create(connection=connection)
        print("Created task {}".format(task.id()))

    def modify(self, args, config, connection):
        task = Task.lookup(connection, args['id'], args['group'])
        task.set_id(args['id'])

        if args['json'] is not None:
            task = self._read(task, args['json'], args['group'])

        task = task.read(connection=connection)

        self._properties(task, args)

        if task.id() != args['id']:
            print("You cannot change the task ID")
            sys.exit(1)

        print("Modify task {}".format(task.id()))
        task.update(connection=connection)

    def delete(self, args, config, connection):
        task = Task(args['id'], args['group'], connection=connection)
        print("Delete task {0}...".format(args['id']))
        task.delete()

    def get(self, args, config, connection):
        task = Task(args['id'], args['group'], connection=connection)
        if not task.exists():
            print("Error: Task does not exist: {0}".format(args['id']))
            sys.exit(1)

        task.read()
        self.jprint(task)

    def _read(self, task, jsonfile, group):
        jf = open(jsonfile).read()
        data = json.loads(jf)

        if task is not None and 'task-type' not in data:
            data['task-type'] = task.type()

        task = Task.unmarshal(data)
        return task
