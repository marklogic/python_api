# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

#
# Copyright 2015 MarkLogic Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
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
# Paul Hoehne       03/09/2015     Initial development
# Paul Hoehne       04/25/2015     Adding check to see if MLCP is already
#                                  in the user path.
#

import os
import time
import logging
from mlcploader import MLCPLoader
from marklogic.models import Connection, Host
from quickstart import SimpleApplication
from requests.auth import HTTPDigestAuth
from resources import TestConnection as tc
import shutil

class LoadContent():
    def __init__(self):
        if os.path.isdir(".mlcp"):
           shutil.rmtree(".mlcp")

    def setup_mlcp(self):
        loader = MLCPLoader()
        loader.clear_directory()
        loader.download_mlcp()

    def load_data(self):
        simpleapp = SimpleApplication(tc.appname, tc.port)

        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        hostname = Host.list(conn)[0]
        exampleapp = simpleapp.create(conn, hostname)

        loader = MLCPLoader()
        loader.load_directory(conn, exampleapp['content'],
                              "data",
                              collections=["example1"], prefix="/test/data1")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)
    logging.getLogger("marklogic.examples").setLevel(logging.INFO)

    loader = LoadContent()
    loader.setup_mlcp()
    loader.load_data()
