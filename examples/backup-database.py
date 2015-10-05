#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script backs up the named databases. Or all databases.

import argparse, json, logging, re, sys, time
from marklogic.exceptions import UnsupportedOperation
from marklogic.connection import Connection
from marklogic.models.database import Database
from marklogic import MarkLogic
from requests.auth import HTTPDigestAuth
from resources import TestConnection as tc

class BackupDatabases:
    def __init__(self):
        self.marklogic       = None
        self.host            = "localhost"
        self.adminuser       = "admin"
        self.adminpass       = "admin"
        self.databases       = None
        self.backup_root     = None
        self.journal_arch    = False
        self.lag_limit       = 30
        self.incremental     = False
        self.max_parallel    = 5
        self.dry_run         = False

    # TODO: better checking of argument types

    def set_host(self, host):
        self.host = host
        return self

    def set_user(self, adminuser):
        self.adminuser = adminuser
        return self

    def set_pass(self, adminpass):
        self.adminpass = adminpass
        return self

    def set_databases(self, databases):
        self.databases = databases

    def set_backup_root(self, directory):
        if directory is not None:
            self.backup_root = directory
            if not self.backup_root.endswith("/"):
                self.backup_root += "/"
        return self

    def set_journal_archiving(self, archiving):
        self.journal_arch = archiving
        return self

    def set_lag_limit(self, limit):
        self.lag_limit = limit
        return self

    def set_incremental(self, incremental):
        self.incremental = incremental
        return self

    def set_max_parallel(self, max_parallel):
        self.max_parallel = max_parallel
        return self

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run
        return self

    def backup_databases(self):
        conn = Connection(self.host,
                          HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        actual_databases = self.marklogic.databases()

        if self.databases is None:
            self.databases = actual_databases

        if self.backup_root is None:
            raise UnsupportedOperation("You must specify the backup root.")

        if self.max_parallel <= 0:
            self.max_parallel = 1

        for dbname in self.databases:
            if not dbname in actual_databases:
                raise UnsupportedOperation("Database does not exist: {0}"
                                           .format(dbname))

        maxp = self.max_parallel
        running = 0
        done = False
        queue = self.databases
        status_list = {}
        min_wait = 5
        max_wait = 30
        wait_incr = 5
        wait = min_wait

        while not done:
            done = True

            while len(queue) > 0 and running < maxp:
                dbname = queue.pop(0)
                running += 1
                done = False

                print("Backing up {0}".format(dbname))
                if not self.dry_run:
                    db = self.marklogic.database(dbname)
                    bkp = db.backup(self.backup_root + dbname, connection=conn)
                    status_list[dbname] = bkp
                    response = bkp.status()
                    if response['status'] != 'in-progress':
                        print("{0}: {1}".format(dbname, response['status']))

            if self.dry_run:
                if running > 0 or len(queue) > 0:
                    print("{0} backups in dry-run; {1} in queue..."
                          .format(running, len(queue)))
                    running = 0
            else:
                if len(status_list) > 0:
                    new_list = {}
                    for dbname in status_list:
                        bkp = status_list[dbname]
                        response = bkp.status()
                        print("{0}: {1}".format(dbname, response['status']))
                        if response['status'] == 'in-progress':
                            done = False
                            new_list[dbname] = bkp
                        else:
                            running -= 1
                            wait = min_wait

                    done = done and len(queue) == 0

                    if not done:
                        status_list = new_list
                        if running < maxp and len(queue) != 0:
                            print("Running: {0} backups running; {1} in queue..."
                                  .format(running, len(queue)))
                            wait = min_wait
                            print("")
                        else:
                            print("Waiting {0}s: {1} backups running; {2} in queue..."
                                  .format(wait, running, len(queue)))
                            time.sleep(wait)
                            if wait < max_wait:
                                wait += wait_incr
                            print("")

def main():
    parser = argparse.ArgumentParser(description="Backup databases")

    parser.add_argument('--host', default='localhost',
                        metavar='HOST',
                        help="The host to use for REST configuration")
    parser.add_argument('--user', default='admin',
                        help='The user for REST configuration')
    parser.add_argument('--password', default='admin',
                        help='The password for REST configuration')
    parser.add_argument('--database', nargs='+',
                        help='The root directory for backups (on the host!)')
    parser.add_argument('--root',
                        help='The root directory for backups (on the host!)')
    parser.add_argument('--journal-archiving', action='store_true',
                        help='Turn on journal archiving')
    parser.add_argument('--incremental', action='store_true',
                        help='Perform incremental backup')
    parser.add_argument('--max-parallel', default=5, type=int,
                        help='Maximum number of backups to run in parallel.')
    parser.add_argument('--lag-limit',
                        help='The lag limit')
    parser.add_argument('--dry-run', action='store_true',
                        help="Just print the JSON, don't actually create forests")
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging')

    args = vars(parser.parse_args())

    backup = BackupDatabases()

    for opt in args:
        arg = args[opt]

        if opt == 'host':
            backup.set_host(arg)
        elif opt == 'user':
            backup.set_user(arg)
        elif opt == 'password':
            backup.set_pass(arg)
        elif opt == 'database':
            backup.set_databases(arg)
        elif opt == 'root':
            backup.set_backup_root(arg)
        elif opt == 'journal_archiving':
            backup.set_journal_archiving(arg)
        elif opt == 'incremental':
            backup.set_incremental(arg)
        elif opt == 'lag_limit':
            backup.set_lag_limit(arg)
        elif opt == 'max_parallel':
            backup.set_max_parallel(arg)
        elif opt == 'database':
            backup.set_database(arg)
        elif opt == 'dry_run':
            backup.set_dry_run(arg)
        elif opt == 'debug':
            pass
        else:
            print("Error: unexpected argument: " + opt)
            sys.exit(1)

    if args['debug']:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("marklogic").setLevel(logging.DEBUG)
        logging.getLogger("marklogic.connection").setLevel(logging.INFO)

    backup.backup_databases()

if __name__ == '__main__':
  main()
