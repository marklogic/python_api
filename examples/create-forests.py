#!/usr/bin/python3

import argparse, json, logging, os, pwd, re, sys
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
from marklogic.models.host import Host
from marklogic.models.forest import Forest
from marklogic.connection import Connection
from marklogic.exceptions import *

class CreateForests:
    def __init__(self):
        self.marklogic       = None
        self.host            = "localhost"
        self.hosts           = None
        self.prefix          = "F"
        self.forests         = 2
        self.start           = 1
        self.failover        = "none"
        self.failhost        = None
        self.adminuser       = "admin"
        self.adminpass       = "admin"
        self.data_dir        = None
        self.large_data_dir  = None
        self.fast_data_dir   = None
        self.database        = None
        self.dry_run         = False

    # TODO: better checking of argument types

    def set_rest_host(self, host):
        self.host = host
        return self

    def set_hosts(self, hosts):
        if hosts is None:
            self.hosts = None
        else:
            if isinstance(hosts, list):
                self.hosts = hosts
            else:
                self.hosts = [ hosts ]
        return self

    def set_prefix(self, prefix):
        self.prefix = prefix
        return self

    def set_forest_count(self, forests):
        self.forests = int(forests)
        return self

    def set_start_number(self, start):
        self.start = start
        return self

    def set_failover(self, failover):
        self.failover = failover
        return self

    def set_failover_host(self, failhost):
        self.failhost = failhost
        return self

    def set_user(self, adminuser):
        self.adminuser = adminuser
        return self

    def set_pass(self, adminpass):
        self.adminpass = adminpass
        return self

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir
        return self

    def set_large_data_dir(self, large_data_dir):
        self.large_data_dir = large_data_dir
        return self

    def set_fast_data_dir(self, fast_data_dir):
        self.fast_data_dir = fast_data_dir
        return self

    def set_database(self, database):
        self.database = database
        return self

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run
        return self

    def create_forests(self):
        conn = Connection(self.host,
                          HTTPDigestAuth(self.adminuser, self.adminpass))
        self.marklogic = MarkLogic(conn)

        if self.failhost is None and self.failover != "none":
            print("Invalid configuration, specify failover-host for failover:",
                  self.failover)
            sys.exit(1)

        if self.hosts is None:
            host_names = self.marklogic.hosts()
        else:
            host_names = self.hosts

        exists = []
        host_index = 0
        for host_name in host_names:
            host_index += 1
            for count in range(1,self.forests + 1):
                name = self.prefix + "-" + str(host_index) + "-" + str(count)
                forest = Forest(name, host_name, conn)
                if forest.exists():
                    exists.append(host_name + ":" + name)

        if len(exists) != 0:
            print("Abort: forest(s) already exist:")
            for f in exists:
                print("   ", f)
            sys.exit(1)

        host_index = 0
        for host_name in host_names:
            host_index += 1
            for count in range(self.start,self.start + self.forests):
                name = self.prefix + "-" + str(host_index) + "-" + str(count)
                forest = Forest(name, host_name, conn)
                if self.data_dir is not None:
                    forest.set_data_directory(self.data_dir)
                if self.large_data_dir is not None:
                    forest.set_large_data_directory(self.large_data_dir)
                if self.fast_data_dir is not None:
                    forest.set_fast_data_directory(self.fast_data_dir)

                if self.failhost is not None:
                    forest.set_failover(self.failover)
                    forest.set_failover_host_names(self.failhost)

                if self.database is not None:
                    forest.set_database(self.database)

                print("Create forest " + name + " on " + host_name)
                if self.dry_run:
                    print(json.dumps(forest.marshal(), sort_keys=True, indent=2))
                else:
                    forest.create()

        print("Finished")

def main():
    parser = argparse.ArgumentParser(description="Create forests on a cluster")

    parser.add_argument('--rest-host', default='localhost',
                        metavar='HOST',
                        help="The host to use for REST configuration")
    parser.add_argument('--host', nargs="*",
                        help='Hosts on which to create forests')
    parser.add_argument('--prefix', default='F',
                        metavar='PFX',
                        help='The prefix for forest names')
    parser.add_argument('--forests', default=2,
                        metavar='COUNT',
                        help='The number of forests per host')
    parser.add_argument('--start-forest', default=1,
                        metavar='FIRST',
                        help='The forest index at which to start numbering')
    parser.add_argument('--failover', default='none',
                        choices=['local','shared','none'],
                        help='Failover configuration')
    parser.add_argument('--failover-host',
                        metavar='HOST',
                        help='For shared-disk failover, use this failover host for all forests')
    parser.add_argument('--user', default='admin',
                        help='The user for REST configuration')
    parser.add_argument('--pass', default='admin',
                        help='The password for REST configuration')
    parser.add_argument('--data-dir',
                        metavar='DIR',
                        help='The data directory')
    parser.add_argument('--large-data-dir',
                        metavar='DIR',
                        help='The large data directory')
    parser.add_argument('--fast-data-dir',
                        metavar='DIR',
                        help='The fast data directory')
    parser.add_argument('--database',
                        help='The database to which forests should be assigned')
    parser.add_argument('--dry-run', action='store_true',
                        help="Just print the JSON, don't actually create forests")
    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging')

    args = vars(parser.parse_args())

    creator = CreateForests()

    for opt in args:
        arg = args[opt]

        if opt == 'rest_host':
            creator.set_rest_host(arg)
        elif opt == 'host':
            creator.set_hosts(arg)
        elif opt == 'prefix':
            creator.set_prefix(arg)
        elif opt == 'forests':
            creator.set_forest_count(arg)
        elif opt == 'start_forest':
            creator.set_start_number(arg)
        elif opt == 'failover':
            creator.set_failover(arg)
        elif opt == 'failover_host':
            creator.set_failover_host(arg)
        elif opt == 'user':
            creator.set_user(arg)
        elif opt == 'pass':
            creator.set_pass(arg)
        elif opt == 'data_dir':
            creator.set_data_dir(arg)
        elif opt == 'large_data_dir':
            creator.set_large_data_dir(arg)
        elif opt == 'fast_data_dir':
            creator.set_fast_data_dir(arg)
        elif opt == 'database':
            creator.set_database(arg)
        elif opt == 'dry_run':
            creator.set_dry_run(arg)
        elif opt == 'debug':
            pass
        else:
            print("Error: unexpected argument: " + opt)
            sys.exit(1)

    if args['debug']:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("marklogic").setLevel(logging.DEBUG)

    creator.create_forests()

if __name__ == '__main__':
  main()
