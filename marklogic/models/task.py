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
# Norman Walsh      22 Mar 2016    Initial development
#

"""
Task related classes for manipulating MarkLogic scheduled tasks
"""

# FIXME: add docstrings
# FIXME: check types of arguments

from abc import ABCMeta
import json
import logging
from marklogic.utilities import PropertyLists
from marklogic.models.model import Model
from marklogic.exceptions import UnexpectedManagementAPIResponse


class Task(Model, PropertyLists):
    """
    The Task class encapsulates a MarkLogic scheduled task.
    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def __init__(self, taskid=None, group="Default", connection=None,
                 save_connection=True):
        """
        Create a scheduled task.
        """
        if taskid is None:
            self._config = {}
        else:
            self._config = {'task-id': taskid}

        self.group = group
        self.taskid = taskid
        self.etag = None
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic.task")

    def set_connection(self, connection, save_connection):
        if save_connection:
            self.connection = connection
        return self

    def id(self):
        return self._get_config_property('task-id')

    def set_id(self, taskid):
        self._config['task-id'] = taskid
        self.taskid = taskid
        return self

    def type(self):
        return self._get_config_property('task-type')

    def set_type(self, tasktype):
        self._config['task-type'] = tasktype
        return self

    def database(self):
        return self._get_config_property('task-database')

    def set_database(self, database):
        self._config['task-database'] = database
        return self

    def enabled(self):
        return self._get_config_property('task-enabled')

    def set_enabled(self, enabled):
        self._config['task-enabled'] = enabled
        return self

    def host(self):
        return self._get_config_property('task-host')

    def set_host(self, host):
        if host is None:
            if 'task-host' in self._config:
                del self._config['task-host']
        else:
            self._config['task-host'] = host
        return self

    def modules(self):
        modules = self._get_config_property('task-modules')
        if modules == "":
            return None
        else:
            return modules

    def set_modules(self, modules):
        if modules is None:
            self._config['task-modules'] = ""
        else:
            self._config['task-modules'] = modules
        return self

    def path(self):
        return self._get_config_property('task-path')

    def set_path(self, path):
        self._config['task-path'] = path
        return self

    def root(self):
        return self._get_config_property('task-root')

    def set_root(self, root):
        self._config['task-root'] = root
        return self

    def priority(self):
        return self._get_config_property('task-priority')

    def set_priority(self, priority):
        if priority is None:
            if 'task-priority' in self._config:
                del self._config['task-priority']
        else:
            self._config['task-priority'] = priority
        return self

    def user(self):
        return self._get_config_property('task-user')

    def set_user(self, user):
        self._config['task-user'] = user
        return self

    @classmethod
    def daily_task(cls, path, start_time, root="/", period=1,
                   user="nobody", host=None, priority=None,
                   modules=None, database="Documents",
                   connection=None, save_connection=True):
        return DailyTask(path, start_time, root=root, period=period,
                         user=user, host=host, priority=priority,
                         modules=modules, database=database,
                         connection=connection,
                         save_connection=save_connection)

    @classmethod
    def hourly_task(cls, path, start_time, root="/", period=1,
                    user="nobody", host=None, priority=None,
                    modules=None, database="Documents",
                    connection=None, save_connection=True):
        return HourlyTask(path, start_time, root=root, period=period,
                          user=user, host=host, priority=priority,
                          modules=modules, database=database,
                          connection=connection,
                          save_connection=save_connection)

    @classmethod
    def minutely_task(cls, path, root="/", period=1,
                      user="nobody", host=None, priority=None,
                      modules=None, database="Documents",
                      connection=None, save_connection=True):
        return MinutelyTask(path, root=root, period=period,
                            user=user, host=host, priority=priority,
                            modules=modules, database=database,
                            connection=connection,
                            save_connection=save_connection)

    @classmethod
    def monthly_task(cls, path, month_day, start_time, root="/", period=1,
                     user="nobody", host=None, priority=None,
                     modules=None, database="Documents",
                     connection=None, save_connection=True):
        return MonthlyTask(path, month_day, start_time, root=root,
                           period=period, user=user, host=host,
                           priority=priority, modules=modules,
                           database=database, connection=connection,
                           save_connection=save_connection)

    @classmethod
    def weekly_task(cls, path, days, start_time, root="/", period=1,
                    user="nobody", host=None, priority=None,
                    modules=None, database="Documents",
                    connection=None, save_connection=True):
        return WeeklyTask(path, days, start_time, root=root, period=period,
                          user=user, host=host, priority=priority,
                          modules=modules, database=database,
                          connection=connection,
                          save_connection=save_connection)

    @classmethod
    def once_task(cls, path, start_date, start_time, root="/",
                  user="nobody", host=None, priority=None,
                  modules=None, database="Documents",
                  connection=None, save_connection=True):
        return OnceTask(path, start_date, start_time, root=root,
                        user=user, host=host, priority=priority,
                        modules=modules, database=database,
                        connection=connection,
                        save_connection=save_connection)

    def create(self, group="Default", connection=None):
        """
        Create a new scheduled task.

        :param connection: The server connection

        :return: The task object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("tasks", parameters=["group-id="+group])

        struct = self.marshal()

        self.logger.debug("Creating {0} task".format(self.type()))

        response = connection.post(uri, payload=struct)

        if response.status_code != 201:
            raise UnexpectedManagementAPIResponse(response.text)

        if 'etag' in response.headers:
            self.etag = response.headers['etag']

        # All well and good, but we need to know what ID was assigned
        location = response.headers['location']
        qpos = location.index("?")
        location = location[0:qpos]

        uri = "{0}://{1}:{2}{3}/properties?group-id={4}" \
              .format(connection.protocol, connection.host,
                      connection.management_port, location, group)

        response = connection.get(uri)

        if response.status_code == 200:
            result = Task.unmarshal(json.loads(response.text))
            self._config = result._config
            self.taskid = self._config['task-id']
            self.group = group
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def read(self, connection=None):
        """
        Loads the task from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server
        :return: The task object
        """
        if connection is None:
            connection = self.connection

        task = Task.lookup(connection, self.taskid, self.group)

        if task is not None:
            self._config = task._config
            self.etag = task.etag

        return self

    def update(self, connection=None):
        """
        Save the configuration changes with the given connection.

        :param connection:The server connection

        :return: The host object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("tasks", self.taskid,
                             parameters=["group-id="+self.group])
        struct = self.marshal()
        response = connection.put(uri, payload=struct, etag=self.etag)
        if response.status_code != 204:
            raise UnexpectedManagementAPIResponse(response.text)

        if 'etag' in response.headers:
            self.etag = response.headers['etag']

        return self

    def delete(self, group="Default", connection=None):
        """
        Remove the given task.

        :param connection: The server connection

        :return: The database object
        """
        if connection is None:
            connection = self.connection

        uri = connection.uri("tasks", self.taskid, properties=None,
                             parameters=["group-id="+group])
        response = connection.delete(uri)
        return self

    def exists(self, connection=None):
        """
        Returns true if (and only if) the task exits.

        :param connection: The connection to the MarkLogic database
        :return: True if the task exists
        """
        if connection is None:
            connection = self.connection

        task = Task.lookup(connection, self.id(), self.group)
        return task is not None

    @classmethod
    def lookup(cls, connection, taskid, group):
        """
        Look up an individual task.

        :param connection: A connection to a MarkLogic server
        :param taskid: The ID of the task
        :return: The task information
        """
        uri = connection.uri("tasks", taskid, parameters=["group-id="+group])
        response = connection.get(uri)
        if response.status_code == 200:
            result = Task.unmarshal(json.loads(response.text))
            if 'etag' in response.headers:
                result.etag = response.headers['etag']
            return result
        else:
            return None

    @classmethod
    def list(cls, connection):
        """
        Lists the IDs of tasks available on this cluster.

        :param connection: A connection to a MarkLogic server
        :return: A list of task IDs.
        """

        uri = connection.uri("tasks")
        response = connection.get(uri)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            task_count = response_json['tasks-default-list']['list-items']['list-count']['value']

            result = []
            if task_count > 0:
                for item in response_json['tasks-default-list']['list-items']['list-item']:
                    result.append(item['idref'])
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    @classmethod
    def unmarshal(cls, config):
        if 'task-type' in config:
            if config['task-type'] == "daily":
                result = DailyTask()
            elif config['task-type'] == "hourly":
                result = HourlyTask()
            elif config['task-type'] == "minutely":
                result = MinutelyTask()
            elif config['task-type'] == "monthly":
                result = MonthlyTask()
            elif config['task-type'] == "weekly":
                result = WeeklyTask()
            elif config['task-type'] == "once":
                result = OnceTask()
            else:
                result = Task()
        else:
            result = Task()

        result._config = config
        if 'task-id' in result._config:
            result.taskid = result._config['task-id']
        else:
            result.taskid = None
        return result

    def marshal(self):
        struct = {}
        for key in self._config:
            struct[key] = self._config[key]
        return struct


class RepeatingTask(Task):
    """
    The RepeatingTask class encapsulates a MarkLogic repeating scheduled task.
    This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def __init__(self, connection=None, save_connection=True):
        super().__init__(connection=connection,
                         save_connection=save_connection)

    def period(self):
        return self._get_config_property('task-period')

    def set_period(self, period):
        self._config['task-period'] = period
        return self


class DailyTask(RepeatingTask):
    """
    The DailyTask class encapsulates a MarkLogic daily scheduled task.
    """
    def __init__(self, path="/", start_time=None, root="/", period=1,
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create a daily scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'daily',
                        'task-enabled': True}
        self.set_path(path)
        self.set_start_time(start_time)
        self.set_root(root)
        self.set_period(period)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)

    def start_time(self):
        return self._get_config_property('task-start-time')

    def set_start_time(self, start_time):
        self._config['task-start-time'] = start_time
        return self


class HourlyTask(RepeatingTask):
    """
    The HourlyTask class encapsulates a MarkLogic hourly scheduled task.
    """
    def __init__(self, path="/", start_time=None, root="/", period=1,
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create an hourly scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'hourly',
                        'task-enabled': True}
        self.set_path(path)
        self.set_start_time(start_time)
        self.set_root(root)
        self.set_period(period)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)

    def start_time(self):
        return self._get_config_property('task-start-time')

    def set_start_time(self, start_time):
        self._config['task-start-time'] = start_time
        return self


class MinutelyTask(RepeatingTask):
    """
    The MinutelyTask class encapsulates a MarkLogic minutely scheduled task.
    """
    def __init__(self, path="/", root="/", period=1,
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create a minutely scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'minutely',
                        'task-enabled': True}
        self.set_path(path)
        self.set_root(root)
        self.set_period(period)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)


class MonthlyTask(RepeatingTask):
    """
    The MonthlyTask class encapsulates a MarkLogic monthly scheduled task.
    """
    def __init__(self, path="/", month_day=None, start_time=None,
                 root="/", period=1,
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create a monthly scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'monthly',
                        'task-enabled': True}
        self.set_path(path)
        self.set_month_day(month_day)
        self.set_start_time(start_time)
        self.set_root(root)
        self.set_period(period)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)

    def month_day(self):
        return self._get_config_property('task-month-day')

    def set_month_day(self, month_day):
        self._config['task-month-day'] = month_day
        return self

    def start_time(self):
        return self._get_config_property('task-start-time')

    def set_start_time(self, start_time):
        self._config['task-start-time'] = start_time
        return self


class WeeklyTask(RepeatingTask):
    """
    The WeeklyTask class encapsulates a MarkLogic weekly scheduled task.
    """
    def __init__(self, path="/", days=None, start_time=None,
                 root="/", period=1,
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create a weekly scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'weekly',
                        'task-enabled': True}
        self.set_path(path)
        self.set_days(days)
        self.set_start_time(start_time)
        self.set_root(root)
        self.set_period(period)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)

    def start_time(self):
        return self._get_config_property('task-start-time')

    def set_start_time(self, start_time):
        self._config['task-start-time'] = start_time
        return self

    def days(self):
        return self._get_config_property('task-day')

    def add_day(self, day):
        return self.add_to_property_list('task-day', day)

    def set_days(self, days):
        return self.set_property_list('task-day', days)


class OnceTask(RepeatingTask):
    """
    The OnceTask class encapsulates a MarkLogic task scheduled once.
    """
    def __init__(self, path="/", start_date=None, start_time=None, root="/",
                 user="nobody", host=None, priority=None,
                 modules=None, database="Documents",
                 connection=None, save_connection=True):
        """
        Create a weekly scheduled task.
        """
        super().__init__(connection=connection,
                         save_connection=save_connection)

        self._config = {'task-type': 'once',
                        'task-enabled': True}
        self.set_path(path)
        self.set_start_date(start_date)
        self.set_start_time(start_time)
        self.set_root(root)
        self.set_user(user)
        self.set_host(host)
        self.set_priority(priority)
        self.set_modules(modules)
        self.set_database(database)

    def start_date(self):
        return self._get_config_property('task-start-date')

    def set_start_date(self, start_date):
        self._config['task-start-date'] = start_date
        return self

    def start_time(self):
        return self._get_config_property('task-start-time')

    def set_start_time(self, start_time):
        self._config['task-start-time'] = start_time
        return self


