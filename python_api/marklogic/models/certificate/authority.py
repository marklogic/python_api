# -*- coding: utf-8 -*-
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
# Norman Walsh      05/13/2015     Hacked user.py into authority.py
#

"""
Authority related classes for manipulating Certificate Authorities
"""

from __future__ import unicode_literals, print_function, absolute_import

import json, requests
from marklogic.exceptions import UnexpectedManagementAPIResponse
from marklogic.utilities.validators import assert_boolean

class Authority:
    """
    The Authority class encapsulates a MarkLogic representation of
    a certificate authority. Certificate authorities are created by
    uploading trusted certificates.
    """
    def __init__(self, certid):
        """
        Create a new certificate authority. Except it doesn't, really.
        It just creates a reference to the certificate authority with the
        specified ID. There's nothing you can do with a certificate
        authority, really.
        """
        self._config = {'id': certid}

    def certificate_id(self):
        """
        The MarkLogic certificate ID for the certificate authority

        :return: The id
        """
        return self._config['certificate-id']

    def enabled(self):
        """
        Is this certificate enabled?

        Certificates that are automatically installed by MarkLogic are
        marked "disabled" when they are deleted (rather than actually
        removing them). This prevents an upgrade from simply re-installing
        them.

        :return: The state of the enabled flag, True or False
        """
        return self._config['enabled']

    def properties(self):
        """
        The properties of the certificate, as a python dictionary. The
        exact properties available depends on the nature of the
        certificate authority.

        :return: The certificate authority properties
        """
        return self._config['cert']

    def marshal(self):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = { }
        for key in self._config:
            struct[key] = self._config[key];
        return struct

    @classmethod
    def unmarshal(cls, config):
        """
        Construct a new Authority from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed User object with the specified properties.
        """
        result = Authority(config['certificate-id'])
        result._config = config
        return result

    @classmethod
    def create(cls, connection, pem):
        """
        Creates a new certificate authority

        Note that this is a class method, you cannot create a certificate
        authority except by uploading a PEM-encoded "certificate authority"
        certificate.

        :param connection: The connection to a MarkLogic server
        :param pem: The PEM-encoded certificate authority certificate

        :return: The Authority object
        """
        uri = "http://{0}:{1}/manage/v2/certificate-authorities" \
          .format(connection.host, connection.management_port)

        response = requests.post(uri, data=pem, auth=connection.auth,
                                 headers={"content-type": "text/plain"})

        if response.status_code not in [200, 201, 204]:
            raise UnexpectedManagementAPIResponse(response.text)

        # All well and good, but we need to know what ID was assigned
        uri = "http://{0}:{1}{2}/properties" \
          .format(connection.host, connection.management_port,
                  response.headers['location'])

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code == 200:
            result = Authority.unmarshal(json.loads(response.text))
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return result

    def read(self, connection):
        """
        Loads the Authority from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server

        :return: The Authority object
        """
        auth = Authority.lookup(self._config['certificate-id'])
        if auth is None:
            return None
        else:
            self._config = auth._config
            return self

    def delete(self, connection):
        """
        Deletes the Authority from the MarkLogic server.

        Note: Authorities have no meaningful identity except their
        MarkLogic certificate id. After deleting an authority, no such
        id exists, so this method returns None.

        :param connection: The connection to a MarkLogic server

        :return: None
        """
        uri = "http://{0}:{1}/manage/v2/certificate-authorities/{2}" \
          .format(connection.host, connection.management_port,
                  self._config['certificate-id'])

        response = requests.delete(uri, auth=connection.auth)

        if (response.status_code not in [200, 204]
            and not response.status_code == 404):
            raise UnexpectedManagementAPIResponse(response.text)

        return None

    @classmethod
    def list(cls, connection, include_names=False):
        """
        List all the certificate authorities.

        If `include_names` is `True`, then the values in the list will be
        structured values consisting of the certificate ID and the certificate
        name separated by a "|".

        :param connection: The connection to a MarkLogic server
        :param include_names: Indicates if structured names should be returned.

        :return: A list of certificate authority IDs.
        """

        uri = "http://{0}:{1}/manage/v2/certificate-authorities" \
          .format(connection.host, connection.management_port)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['certificate-authorities-default-list']['list-items']['list-item']:
            if include_names:
                results.append("{0}|{1}".format(item['idref'], item['nameref']))
            else:
                results.append(item['idref'])
        return results

    @classmethod
    def lookup(cls, connection, certid):
        """
        Look up an individual certificate by certificate id.

        :param connection: The connection to the MarkLogic database
        :param certid: The certificate id

        :return: The Authority object
        """
        uri = "http://{0}:{1}/manage/v2/certificate-authorities/{2}/properties" \
          .format(connection.host, connection.management_port, certid)

        response = requests.get(uri, auth=connection.auth,
                                headers={'accept': 'application/json'})

        if response.status_code == 200:
            result = Authority.unmarshal(json.loads(response.text))
            return result
        elif response.status_code == 404:
            return None
        else:
            raise exceptions.UnexpectedManagementAPIResponse(response.text)
