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

from requests.auth import HTTPDigestAuth

"""
Connection related classes and method to connect to MarkLogic.
"""

class Connection:
    """
    The connection class encapsulates the information to connect to
    a MarkLogic server.  The server (for the purpose of loading data
    or creating databases, will listen on ports 8000 and 8002.
    It depends on the database auth class from the requests package.
    """
    def __init__(self, host, auth, port=8000, management_port=8002):
        self.host = host
        self.port = port
        self.management_port = management_port
        self.auth = auth

    @classmethod
    def make_connection(cls, host, username, password):
        return Connection(host, HTTPDigestAuth(username, password))