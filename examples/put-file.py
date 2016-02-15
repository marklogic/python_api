#!/usr/bin/python3
#
# Copyright 2015 MarkLogic Corporation
#
# This script takes a JSON object that enumerates a set of artifacts and
# applies those changes to the server, creating artifacts if necessary.
#
# See put-json-file.py
#
# For example:
#
# python3 put-json-file
#
# TODO
#
# * Upload a file using a PUT CURL command

__author__ = 'pmb'

from requests.auth import HTTPDigestAuth
from marklogic.connection import Connection

conn = Connection("192.168.200.162", HTTPDigestAuth("admin","admin"))

uri = "http://192.168.200.162:8004/LATEST/config/properties"
data = open("./props.json", 'rb').read()
response = conn.putFile(uri=uri, data=data)
print(response)

uri = "http://192.168.200.162:8004/LATEST/config/transforms/accessControl"
data = open("./accessControl.sjs", 'rb').read()
response = conn.putFile(uri=uri, data=data, content_type="application/vnd.marklogic-javascript")
print(response)
