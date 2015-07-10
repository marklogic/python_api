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
Classes for dealing with scheduled backups
"""

class ScheduledDatabaseBackup:
    """
    A database backup. This is an abstract class.
    """
    def __init__(self):
        raise ValueError("Do not instantiate ScheduledDatabaseBackup directly")

    def backup_id(self):
        """
        The backup id.
        """
        if 'backup-id' in self._config:
            return self._config['backup-id']
        return None

    def backup_enabled(self):
        """
        Backup enabled.
        """
        return self._config['backup-enabled']

    def set_backup_enabled(self, enabled):
        """
        Set backup enabled.
        """
        self._config['backup-enabled'] = assert_type(enabled, bool)
        return self

    def backup_directory(self):
        """
        The backup directory.
        """
        return self._config['backup-directory']

    def set_backup_directory(self, value):
        """
        Set the backup directory.
        """
        self._config['backup-directory'] = value
        return self

    def backup_type(self):
        """
        The backup type.
        """
        return self._config['backup-type']

    def backup_timestamp(self):
        """
        The backup timestamp.
        """
        return self._config['backup-timestamp']

    def max_backups(self):
        """
        The maximum number of backups.
        """
        return self._config['max-backups']

    def set_max_backups(self, value):
        """
        Set the maximum number of backups.
        """
        self._config['max-backups'] = value
        return self

    def backup_security_database(self):
        """
        Backup the security database?
        """
        return self._config['backup-security-database']

    def set_backup_security_database(self, value):
        """
        Set backup the security database.
        """
        self._config['backup-security-database'] = assert_type(value, bool)
        return self

    def backup_schemas_database(self):
        """
        Backup the schema database?
        """
        return self._config['backup-schemas-database']

    def set_backup_schemas_database(self, value):
        """
        Set backup the schema database
        """
        self._config['backup-schemas-database'] = assert_type(value, bool)
        return self

    def backup_triggers_database(self):
        """
        Backup the triggers database?
        """
        return self._config['backup-triggers-database']

    def set_backup_triggers_database(self, value):
        """
        Set backup the triggers database
        """
        self._config['backup-triggers-database'] = assert_type(value, bool)
        return self

    def include_replicas(self):
        """
        Include replicas?
        """
        return self._config['include-replicas']

    def set_include_replicas(self, value):
        """
        Set include replicas.
        """
        self._config['include-replicas'] = assert_type(value, bool)
        return self

    def incremental_backup(self):
        """
        Incremental backup?
        """
        return self._config['incremental-backup']

    def set_incremental_backup(self, value):
        """
        Set incremental backup
        """
        self._config['incremental-backup'] = assert_type(value, bool)
        return self

    def journal_archiving(self):
        """
        Journal archiving?
        """
        return self._config['journal-archiving']

    def set_journal_archiving(self, value):
        """
        Set journal archiving.
        """
        self._config['journal-archiving'] = assert_type(value, bool)
        return self

    def journal_archive_path(self):
        """
        The journal archive path.
        """
        return self._config['journal-archive-path']

    def set_journal_archive_path(self, value):
        """
        Set the journal archive path.
        """
        self._config['journal-archive-path'] = value
        return self

    def journal_archive_lag_limit(self):
        """
        The journal archive lag limit.
        """
        return self._config['journal-archive-lag_limit']

    def set_journal_archive_lag_limit(self, value):
        """
        Set the journal archive lag limit.
        """
        self._config['journal-archive-lag_limit'] = assert_type(value, int)
        return self

    @classmethod
    def minutely(cls, backup_dir, period,
                 max_backups=2, backup_security=True, backup_schemas=True,
                 backup_triggers=True, include_replicas=True,
                 incremental_backup=False, journal_archiving=False,
                 journal_archive_path="", lag_limit=15):
        """
        Create a minutely backup.
        """
        return ScheduledDatabaseBackupMinutely(backup_dir, period,
                                      max_backups, backup_security, backup_schemas,
                                      backup_triggers, include_replicas,
                                      incremental_backup, journal_archiving,
                                      journal_archive_path, lag_limit)

    @classmethod
    def hourly(cls, backup_dir, period, start_time,
               max_backups=2, backup_security=True, backup_schemas=True,
               backup_triggers=True, include_replicas=True,
               incremental_backup=False, journal_archiving=False,
               journal_archive_path="", lag_limit=15):
        """
        Create an hourly backup.
        """
        return ScheduledDatabaseBackupHourly(backup_dir, period, start_time,
                                    max_backups, backup_security, backup_schemas,
                                    backup_triggers, include_replicas,
                                    incremental_backup, journal_archiving,
                                    journal_archive_path, lag_limit)

    @classmethod
    def daily(cls, backup_dir, period, start_time,
              max_backups=2, backup_security=True, backup_schemas=True,
              backup_triggers=True, include_replicas=True,
              incremental_backup=False, journal_archiving=False,
              journal_archive_path="", lag_limit=15):
        """
        Create a daily backup.
        """
        return ScheduledDatabaseBackupDaily(backup_dir, period, start_time,
                                   max_backups, backup_security, backup_schemas,
                                   backup_triggers, include_replicas,
                                   incremental_backup, journal_archiving,
                                   journal_archive_path, lag_limit)

    @classmethod
    def weekly(cls, backup_dir, period, days, start_time,
               max_backups=2, backup_security=True, backup_schemas=True,
               backup_triggers=True, include_replicas=True,
               incremental_backup=False, journal_archiving=False,
               journal_archive_path="", lag_limit=15):
        """
        Create a weekly backup.
        """
        return ScheduledDatabaseBackupWeekly(backup_dir, period, days, start_time,
                                    max_backups, backup_security, backup_schemas,
                                    backup_triggers, include_replicas,
                                    incremental_backup, journal_archiving,
                                    journal_archive_path, lag_limit)

    @classmethod
    def monthly(cls, backup_dir, period, month_day, start_time,
                max_backups=2, backup_security=True, backup_schemas=True,
                backup_triggers=True, include_replicas=True,
                incremental_backup=False, journal_archiving=False,
                journal_archive_path="", lag_limit=15):
        """
        Create a monthly backup.
        """
        return ScheduledDatabaseBackupMonthly(backup_dir, period, month_day, start_time,
                                      max_backups, backup_security, backup_schemas,
                                      backup_triggers, include_replicas,
                                      incremental_backup, journal_archiving,
                                      journal_archive_path, lag_limit)

    @classmethod
    def once(cls, backup_dir, start_date, start_time,
             max_backups=2, backup_security=True, backup_schemas=True,
             backup_triggers=True, include_replicas=True,
             incremental_backup=False, journal_archiving=False,
             journal_archive_path="", lag_limit=15):
        """
        Create a one-time backup.
        """
        return ScheduledDatabaseBackupOnce(backup_dir, start_date, start_time,
                                  max_backups, backup_security, backup_schemas,
                                  backup_triggers, include_replicas,
                                  incremental_backup, journal_archiving,
                                  journal_archive_path, lag_limit)


class ScheduledDatabaseBackupMinutely(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, period,
                 max_backups=2, backup_security=True, backup_schemas=True,
                 backup_triggers=True, include_replicas=True,
                 incremental_backup=False, journal_archiving=False,
                 journal_archive_path="", lag_limit=15):
        """
        Create a minutely backup.
        """
        self._config = {
            'backup-type': 'minutely',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }

    def period(self):
        """
        The period.
        """
        return self._config['backup-period']

class ScheduledDatabaseBackupHourly(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, period, start_time,
                 max_backups=2, backup_security=True, backup_schemas=True,
                 backup_triggers=True, include_replicas=True,
                 incremental_backup=False, journal_archiving=False,
                 journal_archive_path="", lag_limit=15):
        """
        Create an hourly backup.
        """
        self._config = {
            'backup-type': 'hourly',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-start-time': start_time,
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }

    def period(self):
        """
        The period.
        """
        return self._config['backup-period']

    def start_time(self):
        """
        The start time.
        """
        return self._config['backup-start-date']

class ScheduledDatabaseBackupDaily(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, period, start_time,
                 max_backups=2, backup_security=True, backup_schemas=True,
                 backup_triggers=True, include_replicas=True,
                 incremental_backup=False, journal_archiving=False,
                 journal_archive_path="", lag_limit=15):
        """
        Create a daily backup.
        """
        self._config = {
            'backup-type': 'daily',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-period': period,
            'backup-start-time': start_time,
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }

    def period(self):
        """
        The period.
        """
        return self._config['backup-period']

    def start_time(self):
        """
        The start time.
        """
        return self._config['backup-start-date']

class ScheduledDatabaseBackupWeekly(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, period, days, start_time,
                 max_backups, backup_security, backup_schemas,
                 backup_triggers, include_replicas,
                 incremental_backup, journal_archiving,
                 journal_archive_path="", lag_limit=15):
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
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }
        if incremental_backup is not None:
            self._config['incremental-backup'] = incremental_backup

    def period(self):
        """
        The period.
        """
        return self._config['backup-period']

    def days(self):
        """
        The days.
        """
        return self._config['backup-day']

    def start_time(self):
        """
        The start time.
        """
        return self._config['backup-start-time']

class ScheduledDatabaseBackupMonthly(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, period, month_day, start_time,
                 max_backups=2, backup_security=True, backup_schemas=True,
                 backup_triggers=True, include_replicas=True,
                 incremental_backup=False, journal_archiving=False,
                 journal_archive_path="", lag_limit=15):
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
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }

    def period(self):
        """
        The period.
        """
        return self._config['backup-period']

    def month_day(self):
        """
        The day of the month.
        """
        return self._config['backup-month-day']

    def start_time(self):
        """
        The start time.
        """
        return self._config['backup-start-time']

class ScheduledDatabaseBackupOnce(ScheduledDatabaseBackup):
    def __init__(self, backup_dir, start_date, start_time,
                 max_backups, backup_security, backup_schemas,
                 backup_triggers, include_replicas,
                 incremental_backup, journal_archiving,
                 journal_archive_path, lag_limit):
        """
        Create a one-time backup.
        """
        self._config = {
            'backup-type': 'once',
            'backup-enabled': True,
            'backup-directory': backup_dir,
            'backup-start-date': start_date,
            'backup-start-time': start_time,
            'max-backups': max_backups,
            'backup-security-database': backup_security,
            'backup-schemas-database': backup_schemas,
            'backup-triggers-database': backup_triggers,
            'include-replicas': include_replicas,
            'journal-archiving': journal_archiving,
            'journal-archive-path': journal_archive_path,
            'journal-archive-lag-limit': lag_limit
            }
        if incremental_backup is not None:
            self._config['incremental-backup'] = incremental_backup

    def start_date(self):
        """
        The start date.
        """
        return self._config['backup-start-date']

    def start_time(self):
        """
        The start time.
        """
        return self._config['backup-start-date']

