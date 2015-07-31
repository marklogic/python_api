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
# Paul Hoehne       03/03/2015     Initial development
# Norman Walsh      07/10/2015     Hacked at it

from __future__ import unicode_literals, print_function, absolute_import

import sys
import logging

from marklogic.connection import Connection
from marklogic.models.host import Host
from marklogic.models.database import Database
from marklogic.models.forest import Forest
from marklogic.models.server import HttpServer
from requests.auth import HTTPDigestAuth
from resources import TestConnection as tc

class Quickstart():
    def __init__(self):
        pass

    def create(self, conn):
        pass

    def destroy(self):
        pass


class SimpleApplication(Quickstart):
    def __init__(self, app_name, port=8100, forests=3):
        """
        Factory class to create databases with an HTTP server and
        modules database. The parts will be named <app_name>_db for the
        database, <app_name>_modules_db for the modules database, and
        the HTTP server port will be on the given port.

        :param app_name: The base name for the application
        :param port: The port number for the HTTP server
        :param forests: The number of forests
        :return: The initialized object
        """
        Quickstart.__init__(self)

        self.logger = logging.getLogger("marklogic.examples")
        self._db_name = app_name + "_db"
        self._modules_db_name = app_name + "_modules_db"
        self._app_port = port
        self._http_server = app_name + "_http_" + str(port)
        self._forests = [self._db_name + "_forest_" + str(i + 1) for i in range(0, forests)]
        self._modules_forest = self._modules_db_name + "_forest"

    def create(self, conn, hostname='localhost.localdomain'):
        """
        Connects to the server and creates the relevant artifacts,
        including the database, the modules database, and the HTTP
        server.

        :param conn: The server connection
        :return:A map containing the content db, the modules db and the HTTP server.
        """
        self.logger.info("Create simple application")
        data_database = Database(self._db_name, hostname)
        data_database.set_forest_names(self._forests)

        modules_database = Database(self._modules_db_name, hostname)

        server = HttpServer(self._http_server, "Default",
                            self._app_port, self._db_name, self._modules_db_name)
        server.set_modules_database_name(self._modules_db_name)

        data_database.create(conn)
        modules_database.create(conn)
        server.create(conn)

        return {
            u'content': data_database,
            u'modules': modules_database,
            u'server': server
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)
    logging.getLogger("marklogic.examples").setLevel(logging.INFO)

    simpleapp = SimpleApplication(tc.appname, tc.port)
    conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
    hostname = Host.list(conn)[0]
    myapp = simpleapp.create(conn, hostname)
