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
# Paul Hoehne       03/01/2015     Initial development
#

import json
import logging
import requests
import time
from http.client import BadStatusLine
from marklogic.exceptions import UnexpectedManagementAPIResponse
from marklogic.exceptions import UnauthorizedAPIRequest
from requests.auth import HTTPDigestAuth
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from requests.packages.urllib3.exceptions import ProtocolError
from requests.packages.urllib3.exceptions import ReadTimeoutError

"""
Connection related classes and method to connect to MarkLogic.
"""


class Connection:
    """
    The connection class encapsulates the information to connect to
    a MarkLogic server.
    """
    def __init__(self, host, auth,
                 protocol="http", port=8000, management_port=8002,
                 root="manage", version="v2", client_version="v1"):
        self.host = host
        self.auth = auth
        self.protocol = protocol
        self.port = port
        self.management_port = management_port
        self.root = root
        self.version = version
        self.client_version = client_version
        self.logger = logging.getLogger("marklogic.connection")
        self.payload_logger = logging.getLogger("marklogic.connection.payloads")

    # You'd expect parameters to be a dictionary, but then it couldn't
    # have repeated keys, so it's an array.
    def uri(self, relation, name=None,
            protocol=None, host=None, port=None, root=None, version=None,
            properties="/properties", parameters=None):
        if protocol is None:
            protocol = self.protocol
        if host is None:
            host = self.host
        if port is None:
            port = self.management_port
        if root is None:
            root = self.root
        if version is None:
            version = self.version

        if name is None:
            name = ""
        else:
            name = "/" + name
            if properties is not None:
                name = name + properties

        uri = "{0}://{1}:{2}/{3}/{4}/{5}{6}" \
              .format(protocol, host, port, root, version, relation, name)

        if parameters is not None:
            uri = uri + "?" + "&".join(parameters)

        return uri

    def client_uri(self, path, protocol=None, host=None, port=None, version=None):
        if protocol is None:
            protocol = self.protocol
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        if version is None:
            version = self.client_version

        uri = "{0}://{1}:{2}/{3}/{4}" \
              .format(protocol, host, port, version, path)

        return uri

    def view_uri(self, path, protocol=None, host=None, port=None, version=None, view=None):
        if protocol is None:
            protocol = self.protocol
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        if version is None:
            version = self.client_version
        if view is None:
            view = "default"

        uri = "{0}://{1}:{2}/manage/{3}/{4}?view={5}" \
              .format(protocol, host, port, version, path, view)

        return uri

    def head(self, uri, accept="application/json"):
        self.logger.debug("HEAD {0}...".format(uri))
        self.response = requests.head(uri, auth=self.auth)
        return self._response()

    def get(self, uri, accept="application/json", headers=None, parameters=None):
        if headers is None:
            headers = {'accept': accept}
        else:
            headers['accept'] = accept

        self.logger.debug("GET  {0}...".format(uri))
        self.payload_logger.debug("Headers:")
        self.payload_logger.debug(json.dumps(headers, indent=2))

        self.response = requests.get(uri, auth=self.auth, headers=headers, params=parameters)
        return self._response()

    def post(self, uri, payload=None, etag=None, headers=None,
             content_type="application/json", accept="application/json"):

        if headers is None:
            headers = {}

        headers['content-type'] = content_type
        headers['accept'] = accept

        if etag is not None:
            headers['if-match'] = etag

        self.logger.debug("POST {0}...".format(uri))
        self.payload_logger.debug("Headers:")
        self.payload_logger.debug(json.dumps(headers, indent=2))
        if payload is not None:
            self.payload_logger.debug("Payload:")
            if content_type == 'application/json':
                self.payload_logger.debug(json.dumps(payload, indent=2))
            else:
                self.payload_logger.debug(payload)

        if payload is None:
            self.response = requests.post(uri, auth=self.auth, headers=headers)
        else:
            if content_type == "application/json":
                self.response = requests.post(uri, json=payload,
                                              auth=self.auth, headers=headers)
            else:
                self.response = requests.post(uri, data=payload,
                                              auth=self.auth, headers=headers)

        return self._response()

    def put(self, uri, payload=None, etag=None,
            content_type="application/json", accept="application/json"):

        headers = {'content-type': content_type,
                   'accept': accept}
        if etag is not None:
            headers['if-match'] = etag

        self.logger.debug("PUT  {0}...".format(uri))
        self.payload_logger.debug("Headers:")
        self.payload_logger.debug(json.dumps(headers, indent=2))
        if payload is not None:
            self.payload_logger.debug("Payload:")
            if content_type == 'application/json':
                self.payload_logger.debug(json.dumps(payload, indent=2))
            else:
                self.payload_logger.debug(payload)

        if payload is None:
            self.response = requests.put(uri, auth=self.auth, headers=headers)
        else:
            if content_type == "application/json":
                self.response = requests.put(uri, json=payload,
                                             auth=self.auth, headers=headers)
            else:
                self.response = requests.put(uri, data=payload,
                                             auth=self.auth, headers=headers)

        return self._response()

    def delete(self, uri, payload=None, etag=None,
               content_type="application/json", accept="application/json"):

        headers = {'content-type': content_type,
                   'accept': accept}
        if etag is not None:
            headers['if-match'] = etag

        self.logger.debug("DELETE {0}...".format(uri))
        self.payload_logger.debug("Headers:")
        self.payload_logger.debug(json.dumps(headers, indent=2))
        if payload is not None:
            self.payload_logger.debug("Payload:")
            if content_type == 'application/json':
                self.payload_logger.debug(json.dumps(payload, indent=2))
            else:
                self.payload_logger.debug(payload)

        if payload is None:
            self.response = requests.delete(uri, auth=self.auth, headers=headers)
        else:
            self.response = requests.delete(uri, json=payload,
                                            auth=self.auth, headers=headers)

        return self._response()

    def _response(self):
        response = self.response

        self.logger.debug("Status code: {0}".format(response.status_code))
        self.payload_logger.debug(response.text)

        if response.status_code < 300:
            pass
        elif response.status_code == 404:
            pass
        elif response.status_code == 401:
            raise UnauthorizedAPIRequest(response.text)
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        if response.status_code == 202:
            data = json.loads(response.text)
            # restart isn't in data, for example, if you execute a shutdown
            if "restart" in data:
                self.wait_for_restart(data["restart"]["last-startup"][0]["value"])

        return response

    def wait_for_restart(self, last_startup, timestamp_uri="/admin/v1/timestamp"):
        """Wait for the host to restart.

        :param last_startup: The last startup time reported in the
        restart message
        """

        uri = "{0}://{1}:8001{2}".format(self.protocol, self.host,
                                         timestamp_uri)

        done = False
        count = 24
        while not done:
            try:
                self.logger.debug("Waiting for restart of {0}"
                                  .format(self.host))
                response = requests.get(uri, auth=self.auth,
                                        headers={'accept': 'application/json'})
                done = (response.status_code == 200
                        and response.text != last_startup)
            except TypeError:
                self.logger.debug("{0}: {1}".format(response.status_code,
                                                    response.text))
                pass
            except BadStatusLine:
                self.logger.debug("{0}: {1}".format(response.status_code,
                                                    response.text))
                pass
            except ProtocolError:
                self.logger.debug("{0}: {1}".format(response.status_code,
                                                    response.text))
                pass
            except ReadTimeoutError:
                self.logger.debug("ReadTimeoutError error...")
                pass
            except ReadTimeout:
                self.logger.debug("ReadTimeout error...")
                pass
            except ConnectionError:
                self.logger.debug("Connection error...")
                pass
            time.sleep(4)  # Sleep one more time even after success...
            count -= 1

            if count <= 0:
                raise UnexpectedManagementAPIResponse("Restart hung?")

        self.logger.debug("{0} restarted".format(self.host))

    @classmethod
    def make_connection(cls, host, username, password):
        return Connection(host, HTTPDigestAuth(username, password))
