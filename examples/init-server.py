#!/usr/bin/python3
#
# Copyright 2018 MarkLogic Corporation
#

__author__ = 'ndw'

import argparse
import logging
import json
import logging
from marklogic import MarkLogic

class InitServer:
    def __init__(self):
        pass

#logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--host", action='store', default="localhost",
                    help="Management API host")
parser.add_argument("--username", action='store', default="admin",
                    help="User name")
parser.add_argument("--password", action='store', default="admin",
                    help="Password")
parser.add_argument("--wallet", action='store', default="admin",
                    help="Wallet password")
parser.add_argument('--debug', action='store_true',
                    help='Enable debug logging')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)

print("Initialize host {}".format(args.host))
MarkLogic.instance_init(args.host)
print("Initialize admin {}".format(args.host))
MarkLogic.instance_admin(args.host, "public", args.username, args.password, args.wallet)

print("finished")
