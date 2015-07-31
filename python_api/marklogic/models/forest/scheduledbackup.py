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
# Norman Walsh      19 July 2015     Initial development

"""
Classes for dealing with scheduled forest backups
"""

import json, requests
from abc import ABCMeta, abstractmethod
import marklogic.utilities.validators
import marklogic.exceptions
from marklogic.models.model import Model

class ScheduledForestBackup(Model):
    """
    A forest backup. This is an abstract class.
    """
    __metaclass__ = ABCMeta

    def id(self):
        """
        The backup id.
        """
        return self._get_config_property('backup-id')

    def enabled(self):
        """
        Backup enabled.
        """
        return self._get_config_property('backup-enabled')

    def set_enabled(self, enabled):
        """
        Set backup enabled.
        """
        return self._set_config_property('backup-enabled',
                                         assert_type(enabled, bool))

    def directory(self):
        """
        The backup directory.
        """
        return self._get_config_property('backup-directory')

    def set_directory(self, value):
        """
        Set the backup directory.
        """
        return self._set_config_property('backup-directory', value)

    def type(self):
        """
        The backup type.
        """
        return self._get_config_property('backup-type')

    def timestamp(self):
        """
        The backup timestamp.
        """
        return self._get_config_property('backup-timestamp')

    @classmethod
    def minutely(cls, backup_dir, period):
        """
        Create a minutely backup.
        """
        return ScheduledForestBackupMinutely(backup_dir, period)

    @classmethod
    def hourly(cls, backup_dir, period, start_minute):
        """
        Create an hourly backup.
        """
        return ScheduledForestBackupHourly(backup_dir, period, start_minute)

    @classmethod
    def daily(cls, backup_dir, period, start_time):
        """
        Create a daily backup.
        """
        return ScheduledForestBackupDaily(backup_dir, period, start_time)

    @classmethod
    def weekly(cls, backup_dir, period, days, start_time):
        """
        Create a weekly backup.
        """
        return ScheduledForestBackupWeekly(backup_dir, period, days, start_time)

    @classmethod
    def monthly(cls, backup_dir, period, month_day, start_time):
        """
        Create a monthly backup.
        """
        return ScheduledForestBackupMonthly(backup_dir, period,
                                            month_day, start_time)

    @classmethod
    def once(cls, backup_dir, start_date, start_time):
        """
        Create a one-time backup.
        """
        return ScheduledForestBackupOnce(backup_dir, start_date, start_time)

class ScheduledForestBackupMinutely(ScheduledForestBackup):
    def __init__(self, backup_dir, period):
        """
        Create a minutely backup.
        """
        self._config = {
            'backup-type': 'minutely',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period
            }

    def period(self):
        """
        The period.
        """
        return self._get_config_property('backup-period')

class ScheduledForestBackupHourly(ScheduledForestBackup):
    def __init__(self, backup_dir, period, start_minute):
        """
        Create an hourly backup.
        """
        self._config = {
            'backup-type': 'hourly',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-start-time': "00:%02d:00" % start_minute
            }

    def period(self):
        """
        The period.
        """
        return self._get_config_property('backup-period')

    def minute(self):
        """
        The start minute.
        """
        time = self._get_config_property('backup-start-time')
        return time.split(':')[1]

class ScheduledForestBackupDaily(ScheduledForestBackup):
    def __init__(self, backup_dir, period, start_time):
        """
        Create a daily backup.
        """
        self._config = {
            'backup-type': 'daily',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-start-time': start_time,
            }

    def period(self):
        """
        The period.
        """
        return self._get_config_property('backup-period')

    def start_time(self):
        """
        The start time.
        """
        return self._get_config_property('backup-start-time')

class ScheduledForestBackupWeekly(ScheduledForestBackup):
    def __init__(self, backup_dir, period, days, start_time):
        """
        Create a weekly backup.
        """
        self._config = {
            'backup-type': 'weekly',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-day': days,
            'backup-start-time': start_time,
            }

    def period(self):
        """
        The period.
        """
        return self._get_config_property('backup-period')

    def days(self):
        """
        The days.
        """
        return self._get_config_property('backup-day')

    def start_time(self):
        """
        The start time.
        """
        return self._get_config_property('backup-start-time')

class ScheduledForestBackupMonthly(ScheduledForestBackup):
    def __init__(self, backup_dir, period, month_day, start_time):
        """
        Create a monthly backup.
        """
        self._config = {
            'backup-type': 'monthly',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-start-time': start_time,
            'backup-month-day': month_day,
            }

    def period(self):
        """
        The period.
        """
        return self._get_config_property('backup-period')

    def month_day(self):
        """
        The day of the month.
        """
        return self._get_config_property('backup-month-day')

    def start_time(self):
        """
        The start time.
        """
        return self._get_config_property('backup-start-time')

class ScheduledForestBackupOnce(ScheduledForestBackup):
    def __init__(self, backup_dir, start_date, start_time):
        """
        Create a one-time backup.
        """
        self._config = {
            'backup-type': 'once',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-start-date': start_date,
            'backup-start-time': start_time,
            }

    def start_date(self):
        """
        The start date.
        """
        return self._get_config_property('backup-start-date')

    def start_time(self):
        """
        The start time.
        """
        return self._get_config_property('backup-start-date')

