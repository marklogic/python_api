#!/usr/bin/python3
#
# Copyright 2016 MarkLogic Corporation
#
# This script provides examples of deploying files to a MarkLogic database without using MLCP
# This is useful when the Application Servers within MarkLogic have SSL enabled.
#
# For example:
#
# python3 deployFile

__author__ = 'pmb'

import argparse
import os
import requests
from requests.auth import HTTPDigestAuth
from marklogic.connection import Connection
from restloader import RESTLoader

parser = argparse.ArgumentParser()
parser.add_argument("--host", action='store', default="192.168.200.162",
                    help="Management API host")
parser.add_argument("--restPort", action='store', default="8000",
                    help="REST port for modules DB")
parser.add_argument("--protocol", action='store', default="http",
                    help="http or https")
parser.add_argument("--username", action='store', default="admin",
                    help="User name")
parser.add_argument("--password", action='store', default="admin",
                    help="Password")
parser.add_argument("--source", action='store', default="data",
                    help="file or root directory to deploy")
parser.add_argument("--targetUri", action='store', default="/app",
                    help="root path for the files in MarkLogic")
parser.add_argument("--certificate", action='store', default=None,
                    help="root path for the files in MarkLogic")
parser.add_argument("--database", action='store', default=None,
                    help="root path for the files in MarkLogic")
parser.add_argument("--permissions", action='store', default=True,
                    help="Permissions for the files in MarkLogic")
args = parser.parse_args()

source = args.source
targetUri = args.targetUri

conn = Connection(args.host, HTTPDigestAuth(args.username, args.password), args.protocol, verify=args.certificate)
requests.packages.urllib3.disable_warnings()

restLoader = RESTLoader(conn, args.restPort, args.database, args.permissions)

if (source is not None):
    if (os.path.isfile(source)):
        response = restLoader.load_file(source, targetUri)
        if (response.status_code == 201):
            print("CREATED: " + targetUri)
        elif (response.status_code == 204):
            print("UPDATED: " + targetUri)
        else:
            print("Unexpected Response:"+response)
    elif (os.path.isdir(source)):
        restLoader.load_directory(source, targetUri)
    else:
        print("The specified source is either not found or not a file/directory")
else:
    print("You must specify the source file/directory")
print("Complete")