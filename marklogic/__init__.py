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
from marklogic.connection import Connection
from marklogic.models.cluster import LocalCluster
from marklogic.models.host import Host
from marklogic.models.task import Task
from marklogic.models.amp import Amp
from marklogic.models.user import User
from marklogic.models.role import Role
from marklogic.models.group import Group
from marklogic.models.database import Database
from marklogic.models.forest import Forest
from requests.auth import HTTPDigestAuth
from marklogic.models.server import Server, HttpServer, WebDAVServer
from marklogic.models.server import OdbcServer, XdbcServer
from marklogic.exceptions import InvalidAPIRequest, UnexpectedManagementAPIResponse

__version__ = "0.0.20"

class MarkLogic:
    """
    The MarkLogic class represents a local cluster.
    """
    def __init__(self, connection=None, save_connection=True):
        """
        Create a MarkLogic object.
        """
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None
        self.logger = logging.getLogger("marklogic")

    def cluster(self, connection=None):
        """
        Get information about the local cluster.
        """
        if connection is None:
            cluster = LocalCluster(self.connection, self.save_connection)
        else:
            cluster = LocalCluster(connection, False)

        return cluster.read()

    def groups(self, connection=None):
        """
        Get a list of the groups in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Group.list(connection)

    def group(self, group_name, connection=None):
        """
        Get the named group.
        """
        if connection is None:
            group = Group(group_name, self.connection, self.save_connection)
        else:
            group = Group(group_name, connection, False)

        return group.read()

    def hosts(self, connection=None):
        """
        Get a list of the hosts in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Host.list(connection)

    def host(self, host_name, connection=None):
        """
        Get the named host.
        """
        if connection is None:
            host = Host(host_name, self.connection, self.save_connection)
        else:
            host = Host(host_name, connection, False)

        return host.read()

    def databases(self, connection=None):
        """
        Get a list of the databases in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Database.list(connection)

    def database(self, database_name, host=None, connection=None):
        """
        Get the named database.
        """
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
        """
        Get a list of the forests in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Forest.list(connection)

    def forest(self, forest_name, host=None, connection=None):
        """
        Get the named forest.
        """
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
        """
        Get a list of the servers in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Server.list(connection)

    def http_servers(self, connection=None):
        """
        Get a list of the HTTP servers in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return HttpServer.list(connection)

    def http_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        """
        Get the named HTTP server.
        """
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
        """
        Get a list of the ODBC servers in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return OdbcServer.list(connection)

    def odbc_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        """
        Get the named ODBC server.
        """
        if connection is None:
            server = OdbcServer(name, group, port, root,
                                content_db_name, modules_db_name,
                                connection=self.connection,
                                save_connection=self.save_connection)
        else:
            server = OdbcServer(name, group, port, root,
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
        """
        Get a list of the XDBC servers in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return XdbcServer.list(connection)

    def xdbc_server(self, name, group='Default', port=0, root='/',
                    content_db_name=None, modules_db_name=None,
                    connection=None):
        """
        Get the named XDBC server.
        """
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
        """
        Get a list of the WebDAV servers in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return WebDAVServer.list(connection)

    def webdav_server(self, name, group='Default', port=0, root='/',
                      content_db_name=None, connection=None):
        """
        Get the named WebDAV server.
        """
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

    def users(self, connection=None):
        """
        Get a list of the users in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return User.list(connection)

    def user(self, user_name, password=None, connection=None):
        """
        Get the named user.
        """
        if connection is None:
            connection = self.connection
            user = User(user_name, password, self.connection, self.save_connection)
        else:
            user = User(user_name, password, connection, False)

        return user.read(connection)

    def roles(self, connection=None):
        """
        Get a list of the roles in the local cluster.
        """
        if connection is None:
            connection = self.connection

        return Role.list(connection)

    def role(self, role_name, connection=None):
        """ Get the named role. """
        if connection is None:
            connection = self.connection
            role = Role(role_name, connection)
        else:
            role = User(role_name, connection, False)

        return role.read(connection)

    def tasks(self, connection=None):
        """
        Get a list of the scheduled tasks.
        """
        if connection is None:
            connection = self.connection

        return Task.list(connection)

    def task(self, taskid, group="Default", connection=None):
        """
        Get the task with a particular task-id.
        """
        if connection is None:
            task = Task.lookup(self.connection, taskid, group)
            task.set_connection(self.connection, self.save_connection)
        else:
            task = Task.lookup(connection, taskid, group)

        return task

    def amps(self, connection=None):
        """
        Get a list of amps.
        """
        if connection is None:
            connection = self.connection

        return Amp.list(connection)

    def amp(self, local_name=None, namespace=None, document_uri=None, \
                connection=None):
        """
        Get a particular amp.
        """
        if connection is None:
            amp = Amp.lookup(self.connection, local_name, namespace, document_uri)
            amp.set_connection(self.connection, self.save_connection)
        else:
            amp = Amp.lookup(connection, local_name, namespace, document_uri)

        return amp

    # =================================================================

    @classmethod
    def instance_init(cls, host):
        """
        Performs first-time initialization of a newly installed server.

        :param host: The name or IP address of the host to initialize
        """
        conn = Connection(host, None)

        uri = "{0}://{1}:8001/admin/v1/init".format(conn.protocol, conn.host)

        logger = logging.getLogger("marklogic")
        logger.debug("Initializing {0}".format(host))

        # This call is a little odd; we special case the 400 error that
        # occurs if the host has alreadya been initialized.
        try:
            response = conn.post(uri,
                                 content_type='application/x-www-form-urlencoded')
        except UnexpectedManagementAPIResponse:
            response = conn.response
            if response.status_code == 400:
                err = json.loads(response.text)
                if "errorResponse" in err:
                    if "messageCode" in err["errorResponse"]:
                        if err["errorResponse"]["messageCode"] == "MANAGE-ALREADYINIT":
                            return Host(host)
            raise

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        return Host(host)._set_just_initialized()

    @classmethod
    def instance_admin(cls,host,realm,admin,password,wallet_password=None):
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

        if wallet_password is not None:
            payload["wallet-password"] = wallet_password

        uri = "{0}://{1}:8001/admin/v1/instance-admin".format(
            conn.protocol, conn.host)

        logger = logging.getLogger("marklogic")
        logger.debug("Initializing security for {0}".format(host))

        # N.B. Can't use conn.post here because we don't need auth yet
        response = requests.post(uri, json=payload,
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'})

        if response.status_code != 202:
            raise UnexpectedManagementAPIResponse(response.text)

        # From now on connections require auth...
        conn = Connection(host, HTTPDigestAuth(admin, password))
        data = json.loads(response.text)
        conn.wait_for_restart(data["restart"]["last-startup"][0]["value"])
