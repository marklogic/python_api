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

import requests
import json
from marklogic.models.utilities.validators import *
from marklogic.models.utilities.exceptions import *

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
        self.settings = {}

    @classmethod
    def backup(cls, conn, database_name, backup_dir, forests=None,
               journal_archiving=False, journal_archive_path=None,
               lag_limit=30,
               incremental=False, incremental_dir=None):
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

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        result = json.loads(response.text)
        host_name = None
        if 'host-name' in result:
            host_name = result['host-name']
        backup = DatabaseBackup(result['job-id'], database_name, host_name)

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

    def status(self, conn):
        """
        The status of the backup job.
        """
        payload = {
            'operation': 'backup-status',
            'job-id': self.job_id
            }

        if self.host_name is not None:
            payload['host-name'] = self.host_name

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)

    def cancel(self, conn):
        """
        Request to cancel the backup job.
        """
        payload = {
            'operation': 'backup-cancel',
            'job-id': self.job_id
            }

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)

    def validate(self, conn):
        """
        Validate the (completed) backup job.
        """
        payload = {
            'operation': 'backup-validate'
            }
        for key in self.settings:
            payload[key] = self.settings[key]

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)

    def purge(self, conn, keep_num=3, backup_dir=None):
        """
        Purge old backups.
        """
        if backup_dir is None:
            backup_dir = self.settings['backup-dir']
        payload = {
            'operation': 'backup-purge',
            'backup-dir': backup_dir,
            'keep-num-backups': assert_type(keep_num, int)
            }

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

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
        self.settings = {}

    @classmethod
    def restore(cls, conn, database_name, backup_dir, forests=None,
                journal_archiving=False, journal_archive_path=None,
                incremental=False, incremental_dir=None):
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

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        result = json.loads(response.text)
        host_name = None
        if 'host-name' in result:
            host_name = result['host-name']
        restore = DatabaseRestore(result['job-id'], database_name, host_name)

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

    def status(self, conn):
        """
        The restore status.
        """
        payload = {
            'operation': 'restore-status',
            'job-id': self.job_id
            }

        if self.host_name is not None:
            payload['host-name'] = self.host_name

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)

    def cancel(self, conn):
        """
        Request to cancel the restore.
        """
        payload = {
            'operation': 'restore-cancel',
            'job-id': self.job_id
            }

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)

    def validate(self, conn):
        """
        Validate a (completed) restore.
        """
        payload = {
            'operation': 'restore-validate'
            }
        for key in self.settings:
            payload[key] = self.settings[key]

        uri = "http://{0}:{1}/manage/v2/databases/{2}" \
          .format(conn.host, conn.management_port, self.database_name)

        response = requests.post(uri, json=payload, auth=conn.auth,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code > 299:
            raise UnexpectedManagementAPIResponse(response.text)

        return json.loads(response.text)
