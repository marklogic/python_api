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

import json
from marklogic.utilities.validators import *
from marklogic.exceptions import *

class DatabaseBackup:
    """
    The DatabaseBackup class represents a backup job that is running
    on the server.
    """
    def __init__(self, job_id, database_name, host_name=None):
        """
        Instantiate a database backup job. This constructor is used internally,
        it should never be called directly. Use the `backup` class
        method instead.
        """
        self.job_id = job_id
        self.database_name = database_name
        self.host_name = host_name
        self.connection = None
        self.settings = {}

    def marshal(self):
        struct = { }
        struct['job-id'] = self.job_id
        struct['database-name'] = self.database_name
        if self.host_name != None:
            struct['host-name'] = self.host_name
        for key in self.settings:
            struct[key] = self.settings[key]
        return struct

    def job_id(self):
        return self.job_id

    @classmethod
    def unmarshal(cls, settings):
        result = DatabaseBackup(None, None)
        for key in settings:
            if key == 'job-id':
                result.job_id = settings[key]
            elif key == 'database-name':
                result.database_name = settings[key]
            elif key == 'host-name':
                result.host_name = settings[key]
            else:
                result.settings[key] = settings[key]
        return result

    @classmethod
    def backup(cls, connection, database_name, backup_dir, forests=None,
               journal_archiving=False, journal_archive_path=None,
               lag_limit=30, incremental=False, incremental_dir=None,
               save_connection=True):
        """
        Start a backup on the server and return an object that represents
        that job.
        """
        payload = {
            'operation': 'backup-database',
            'backup-dir': backup_dir,
            'journal-archiving': assert_type(journal_archiving, bool),
            'lag-limit': assert_type(lag_limit, int),
            'incremental': assert_type(incremental, bool),
            }

        if forests is not None:
            payload['forest'] = assert_list_of_type(forests, str)

        if journal_archiving:
            payload['journal-archive-path'] \
              = assert_type(journal_archive_path, str)

        if incremental:
            payload['incremental-dir'] = assert_type(incremental_dir, str)

        uri = connection.uri("databases", database_name, properties=None)
        response = connection.post(uri, payload=payload)

        result = json.loads(response.text)
        host_name = None
        if 'host-name' in result:
            host_name = result['host-name']
        backup = DatabaseBackup(result['job-id'], database_name, host_name)

        if save_connection:
            backup.connection = connection

        backup.settings = {
            'backup-dir': backup_dir,
            'journal-archiving': assert_type(journal_archiving, bool),
            'lag-limit': assert_type(lag_limit, int),
            'incremental': assert_type(incremental, bool),
            }

        if forests is not None:
            backup.settings['forest'] = assert_list_of_type(forests, str)

        if journal_archiving:
            backup.settings['journal-archive-path'] \
              = assert_type(journal_archive_path, str)

        if incremental:
            backup.settings['incremental-dir'] = assert_type(incremental_dir, str)

        return backup

    def status(self, connection=None):
        """
        The status of the backup job.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'backup-status',
            'job-id': self.job_id
            }

        if self.host_name is not None:
            payload['host-name'] = self.host_name

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

    def cancel(self, connection=None):
        """
        Request to cancel the backup job.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'backup-cancel',
            'job-id': self.job_id
            }

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

    def validate(self, connection=None):
        """
        Validate the (completed) backup job.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'backup-validate'
            }
        for key in self.settings:
            payload[key] = self.settings[key]

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

    def purge(self, connection=None, keep_num=3, backup_dir=None):
        """
        Purge old backups.
        """
        if connection is None:
            connection = self.connection

        if backup_dir is None:
            backup_dir = self.settings['backup-dir']

        payload = {
            'operation': 'backup-purge',
            'backup-dir': backup_dir,
            'keep-num-backups': assert_type(keep_num, int)
            }

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

class DatabaseRestore:
    """
    The DatabaseRestore class represents a restore job that is running
    on the server.
    """
    def __init__(self, job_id, database_name, host_name=None):
        """
        Instantiate a database restore job. This constructor is used internally,
        it should never be called directly. Use the `restore` class
        method instead.
        """
        self.job_id = job_id
        self.database_name = database_name
        self.host_name = host_name
        self.connection = None
        self.settings = {}

    @classmethod
    def restore(cls, connection, database_name, backup_dir, forests=None,
                journal_archiving=False, journal_archive_path=None,
                incremental=False, incremental_dir=None, save_connection=True):
        """
        Start a restore on the server and return an object that represents
        that job.
        """
        payload = {
            'operation': 'restore-database',
            'backup-dir': backup_dir,
            'journal-archiving': assert_type(journal_archiving, bool),
            'incremental': assert_type(incremental, bool),
            }

        if forests is not None:
            payload['forest'] = assert_list_of_type(forests, str)

        if journal_archiving:
            payload['journal-archive-path'] \
              = assert_type(journal_archive_path, str)

        if incremental:
            payload['incremental-dir'] = assert_type(incremental_dir, str)

        uri = connection.uri("databases", database_name, properties=None)
        response = connection.post(uri, payload=payload)

        result = json.loads(response.text)
        host_name = None
        if 'host-name' in result:
            host_name = result['host-name']
        restore = DatabaseRestore(result['job-id'], database_name, host_name)

        if save_connection:
            restore.connection = connection

        restore.settings = {
            'backup-dir': backup_dir,
            'journal-archiving': assert_type(journal_archiving, bool),
            'incremental': assert_type(incremental, bool),
            }

        if forests is not None:
            restore.settings['forest'] = assert_list_of_type(forests, str)

        if journal_archiving:
            restore.settings['journal-archive-path'] \
              = assert_type(journal_archive_path, str)

        if incremental:
            restore.settings['incremental-dir'] = assert_type(incremental_dir, str)

        return restore

    def status(self, connection=None):
        """
        The restore status.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'restore-status',
            'job-id': self.job_id
            }

        if self.host_name is not None:
            payload['host-name'] = self.host_name

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

    def cancel(self, connection=None):
        """
        Request to cancel the restore.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'restore-cancel',
            'job-id': self.job_id
            }

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)

    def validate(self, connection=None):
        """
        Validate a (completed) restore.
        """
        if connection is None:
            connection = self.connection

        payload = {
            'operation': 'restore-validate'
            }
        for key in self.settings:
            payload[key] = self.settings[key]

        uri = connection.uri("databases", self.database_name, properties=None)
        response = connection.post(uri, payload=payload)

        return json.loads(response.text)
