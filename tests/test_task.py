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
# Paul Hoehne       03/26/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models.task import Task, DailyTask, HourlyTask, MinutelyTask
from marklogic.models.task import MonthlyTask, WeeklyTask, OnceTask
from marklogic.exceptions import UnexpectedManagementAPIResponse

class TestTask(MLConfig):
    def test_list_tasks(self):
        tasks = Task.list(self.connection)
        assert True

    def test_daily_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.daily_task("/daily.xqy", "12:34:56Z", connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, DailyTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None

    def test_hourly_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.hourly_task("/hourly.xqy", "12:34:56Z", connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, HourlyTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None

    def test_minutely_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.minutely_task("/minutely.xqy", connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, MinutelyTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None

    def test_monthly_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.monthly_task("/monthly.xqy", 15, "12:34:46Z", \
                                    connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, MonthlyTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None

    def test_weekly_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.weekly_task("/weekly.xqy", ["monday"], "12:34:46Z", \
                                    connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, WeeklyTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None

    def test_once_task(self):
        beforeTasks = Task.list(self.connection)
        task = Task.once_task("/once.xqy", "2017-01-01", "12:34:46Z", \
                                    connection=self.connection)
        task.create()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) > len(beforeTasks)
        assert task.id() is not None
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert isinstance(newTask, OnceTask)

        for key in task._config:
            assert newTask._config[key] == task._config[key]

        task.set_enabled(False)
        task.update()

        task.set_period(3)
        try:
            task.update()
        except UnexpectedManagementAPIResponse:
            pass
        except:
            raise

        task.delete()
        afterTasks = Task.list(self.connection)
        assert len(afterTasks) == len(beforeTasks)
        newTask = Task.lookup(self.connection, task.id(), "Default")
        assert newTask is None
