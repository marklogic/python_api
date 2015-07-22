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

"""
A MarkLogic server
"""

import logging
import requests
import json
import logging
from marklogic.models.connection import Connection
from marklogic.models.cluster import Cluster
from marklogic.models.host import Host
from marklogic.models.database import Database
from marklogic.models.forest import Forest
from requests.auth import HTTPDigestAuth
from marklogic.models.server import Server, HttpServer, WebDAVServer
from marklogic.models.server import OdbcServer, XdbcServer, WebDAVServer

from marklogic.models.utilities.exceptions import *

class MarkLogic:
    """
    The server class provides methods for manipulating a server cluster
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create a server object
        """
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic")

    def cluster(self, connection=None):
        if connection is None:
            cluster = Cluster(self.connection, self.save_connection)
        else:
            cluster = Cluster(connection, False)

        return cluster.read()

    def hosts(self, connection=None):
        if connection is None:
            connection = self.connection

        return Host.list(connection)

    def host(self, host_name, connection=None):
        if connection is None:
            host = Host(host_name, self.connection, self.save_connection)
        else:
            host = Host(host_name, connection, False)

        return host.read()

    def databases(self, connection=None):
        if connection is None:
            connection = self.connection

        return Database.list(connection)

    def database(self, database_name, host=None, connection=None):
        if host is None:
            if connection is None:
                db = Database(database_name, connection=self.connection,
                              save_connection=self.save_connection)
            else:
                db = Database(database_name, connection=connection,
                              save_connection=False)
        else:
            if connection is None:
                db = Database(database_name, host.host_name(),
                              connection=self.connection,
                              save_connection=self.save_connection)
            else:
                db = Database(database_name, host.host_name(),
                              connection=connection,
                              save_connection=False)

        if connection is None:
            return db.read(self.connection)
        else:
            return db.read(connection)

    def forests(self, connection=None):
        if connection is None:
            connection = self.connection

        return Forest.list(connection)

    def forest(self, forest_name, host=None, connection=None):
        if host is None:
            if connection is None:
                db = Forest(forest_name, connection=self.connection,
                            save_connection=self.save_connection)
            else:
                db = Forest(forest_name, connection=connection,
                            save_connection=False)
        else:
            if connection is None:
                db = Forest(forest_name, host.host_name(),
                              connection=self.connection,
                              save_connection=self.save_connection)
            else:
                db = Forest(forest_name, host.host_name(),
                              connection=connection,
                              save_connection=False)

        if connection is None:
            return db.read(self.connection)
        else:
            return db.read(connection)

    def servers(self, connection=None):
        if connection is None:
            connection = self.connection

        return Server.list(connection)

    def http_servers(self, connection=None):
        if connection is None:
            connection = self.connection

        return HttpServer.list(connection)

    def http_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        if connection is None:
             server = HttpServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=self.connection,
                                 save_connection=self.save_connection)
        else:
             server = HttpServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=connection, save_connection=False)

        if connection is None:
            server = server.read(self.connection)
        else:
            server = server.read(connection)

        if server.server_type() != 'http':
            raise InvalidAPIRequest("Attempt to load {0} server as http" \
                                    .format(server.server_type()))

        return server

    def odbc_servers(self, connection=None):
        if connection is None:
            connection = self.connection

        return OdbcServer.list(connection)

    def odbc_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        if connection is None:
             server = OdbcServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=self.connection,
                                 save_connection=self.save_connection)
        else:
             server = OcbcServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=connection, save_connection=False)

        if connection is None:
            server = server.read(self.connection)
        else:
            server = server.read(connection)

        if server.server_type() != 'odbc':
            raise InvalidAPIRequest("Attempt to load {0} server as odbc" \
                                    .format(server.server_type()))

        return server

    def xdbc_servers(self, connection=None):
        if connection is None:
            connection = self.connection

        return XdbcServer.list(connection)

    def xdbc_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        if connection is None:
             server = XdbcServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=self.connection,
                                 save_connection=self.save_connection)
        else:
             server = XdbcServer(name, group, port, root,
                                 content_db_name, modules_db_name,
                                 connection=connection, save_connection=False)

        if connection is None:
            server = server.read(self.connection)
        else:
            server = server.read(connection)

        if server.server_type() != 'xdbc':
            raise InvalidAPIRequest("Attempt to load {0} server as xdbc" \
                                    .format(server.server_type()))

        return server

    def webdav_servers(self, connection=None):
        if connection is None:
            connection = self.connection

        return WebDAVServer.list(connection)

    def webdav_server(self, name, group='Default', port=0, root='/',
                      content_db_name=None, connection=None):
        if connection is None:
             server = WebDAVServer(name, group, port, root,
                                   content_db_name,
                                   connection=self.connection,
                                   save_connection=self.save_connection)
        else:
             server = WebDAVServer(name, group, port, root,
                                   content_db_name,
                                   connection=connection, save_connection=False)

        if connection is None:
            server = server.read(self.connection)
        else:
            server = server.read(connection)

        if server.server_type() != 'webdav':
            raise InvalidAPIRequest("Attempt to load {0} server as webdav" \
                                    .format(server.server_type()))

        return server

    # =================================================================

    @classmethod
    def instance_init(cls,host):
        """
        Performs first-time initialization of a newly installed server.

        :param host: The name or IP address of the host to initialize
        """
        conn = Connection(host, None)

        uri = "http://{0}:8001/admin/v1/init".format(conn.host)

        logger = logging.getLogger("marklogic")
        logger.debug("Initializing {0}".format(host))
        response = requests.post(uri, auth=conn.auth,
                                 headers={'content-type':
                                          'application/x-www-form-urlencoded',
                                          'accept':
                                          'application/json'})

        if response.status_code == 401:
            raise UnauthorizedAPIRequest(response.text)

        if response.status_code == 400:
            err = json.loads(response.text)
            if "errorResponse" in err:
                if "messageCode" in err["errorResponse"]:
                    if err["errorResponse"]["messageCode"] == "MANAGE-ALREADYINIT":
                        return Host(host)

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        data = json.loads(response.text)
        Host.wait_for_restart(conn, data["restart"]["last-startup"][0]["value"])
        return Host(host)._set_just_initialized()

    @classmethod
    def instance_admin(cls,host,realm,admin,password):
        """
        Initializes the security database of a newly initialized server.

        :param host: The name or IP address of the host to initialize
        :param realm: The security realm to install
        :param admin: The name of the admin user
        :param password: The password of the admin user
        """
        conn = Connection(host, None)

        payload = {
            'admin-username': admin,
            'admin-password': password,
            'realm': realm
            }

        uri = "http://{0}:8001/admin/v1/instance-admin".format(conn.host)

        logger = logging.getLogger("marklogic")
        logger.debug("Initializing security for {0}".format(host))
        response = requests.post(uri, json=payload,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        # From now on connections require auth...
        conn = Connection(host, HTTPDigestAuth(admin, password))
        data = json.loads(response.text)
        Host.wait_for_restart(conn, data["restart"]["last-startup"][0]["value"])