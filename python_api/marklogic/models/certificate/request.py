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
# Norman Walsh      05/13/2015     Hacked user.py into request.py
#

"""
Request related classes for manipulating Certificate Requests
"""

from __future__ import unicode_literals, print_function, absolute_import

import json
from marklogic.models.model import Model
from marklogic.utilities.validators import validate_custom

class Request(Model):
    """
    The Request class encapsulates a MarkLogic representation of
    a certificate request.
    """
    def __init__(self, version=0, countryName=None, stateOrProvinceName=None,
                 localityName=None, organizationName=None,
                 organizationalUnitName=None, emailAddress=None,
                 v3ext=None):
        """
        Create a new certificate request.

        The names of the arguments are taken directly from the X509
        form. If specified, v3ext must be a dictionary.

        The `organizationName` is required. You should fill in as many of
        these fields as possible because individual certificate authorities
        have specific requirements for which fields must have values.
        If a required field is missing, a certificate authority will
        typically reject your certificate request with a cryptic error
        message that your request is bad.
        """
        if organizationName is None:
            validate_custom("organizationName is required")

        self._config = {
            'version': version,
            }

        subject = { 'organizationName': organizationName }

        if countryName is not None:
            subject['countryName'] = countryName

        if stateOrProvinceName is not None:
            subject['stateOrProvinceName'] = stateOrProvinceName

        if localityName is not None:
            subject['localityName'] = localityName

        if organizationName is not None:
            subject['organizationName'] = organizationName

        if organizationalUnitName is not None:
            subject['organizationalUnitName'] = organizationalUnitName

        if emailAddress is not None:
            subject['emailAddress'] = emailAddress

        self._config['subject'] = subject

        if v3ext is not None:
            self._config['v3ext'] = v3ext

    def version(self):
        """
        The version.

        :return The current version.
        """
        return self._get_config_property('version')

    def set_version(self, value):
        """
        Set the version.

        :param value: The version.

        :return: The Request object.
        """
        self._config['version'] = value
        return self

    def countryName(self):
        """
        The country.

        :return: The current country.
        """
        return self._get_config_property('subject')['countryName']

    def set_countryName(self, value):
        """
        Set the country.

        :param value: The two character country code (e.g., "US").

        :return: The Request object.
        """
        self._config['subject']['countryName'] = value
        return self

    def stateOrProvinceName(self):
        """
        The state or privince.

        :return: The current state or province
        """
        return self._get_config_property('subject')['stateOrProvinceName']

    def set_stateOrProvinceName(self, value):
        """
        Set the state province

        :param value: The name of the state or province your server in.

        :return: The Request object
        """
        self._config['subject']['stateOrProvinceName'] = value
        return self

    def localityName(self):
        """
        The locality.

        :return: The current locality.
        """
        return self._get_config_property('subject')['localityName']

    def set_localityName(self, value):
        """
        Set the locality.

        :param value: The city your server in.

        :return: The Request object
        """
        self._config['subject']['localityName'] = value
        return self

    def organizationName(self):
        """
        The organization name.

        :return: The current organization name.
        """
        return self._get_config_property('subject')['organizationName']

    def set_organizationName(self, value):
        """
        Set the organization name.

        All certificate requests must include an organization name.

        :param value: The organization or company that owns your server.

        :return: The Request object
        """
        self._config['subject']['organizationName'] = value
        return self

    def organizationalUnitName(self):
        """
        The organizational unit name.

        :return: the current organizational unit name.
        """
        return self._get_config_property('subject')['organizationalUnitName']

    def set_organizationalUnitName(self, value):
        """
        Set the organizational unit name.

        :param value: The organizational unit that operates your server.

        :return: The Request object
        """
        self._config['subject']['organizationalUnitName'] = value
        return self

    def emailAddress(self):
        """
        The contact email address.

        :return: The current contact email address.
        """
        return self._get_config_property('subject')['emailAddress']

    def set_emailAddress(self, value):
        """
        Set the contact email address.

        :param value: The email address to contact regarding your server.

        :return: The Request object
        """
        self._config['subject']['emailAddress'] = value
        return self

    def v3ext(self):
        """
        The X.509v3 extensions.

        :return: The current X.509v3 extensions.
        """
        return self._get_config_property('v3ext')

    def set_v3ext(self, value):
        """
        Set the X.509v3 extensions.

        This value should be a (possibly nested) dictionary, for example:

        ````
        {
          "nsCertType": {
            "critical": false,
            "value": "SSL Server"
          },
          "subjectKeyIdentifier": {
            "critical": false,
            "value": "B2:2C:0C:F8:5E:A7:44:B7"
        }
        ````

        :param value: The X.590v3 extensions dictionary

        :return: The Request object
        """
        self._config['v3ext'] = value
        return self

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
        Construct a new Request from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed User object with the specified properties.
        """
        result = Request(organizationName="temp")
        result._config = config
        return result
