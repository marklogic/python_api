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
# Norman Walsh      05/13/2015     Hacked user.py into template.py
#

"""
Template related classes for manipulating Certificate Templates
"""

from __future__ import unicode_literals, print_function, absolute_import

import json
from marklogic.exceptions import UnexpectedManagementAPIResponse
from marklogic.utilities.validators import assert_type
from marklogic.utilities.validators import validate_custom
from marklogic.models.certificate.request import Request
from marklogic.models.model import Model

class Template(Model):
    """
    The Template class encapsulates a MarkLogic representation of
    a certificate template.
    """
    def __init__(self, name, description, cert_request,
                 key_type="rsa", key_length=None, pass_phrase=None,
                 connection=None, save_connection=None):
        """
        Create a new certificate template.
        """
        self._config = {
            "template-name": name,
            "template-description": description,
            "req": assert_type(cert_request, Request)
            }

        if key_type is not None:
            self._config['key-type'] = key_type

        if key_length is not None or pass_phrase is not None:
            options = {}
            if key_length is not None:
                options['key-length'] = key_length
            if pass_phrase is not None:
                optoins['pass-phrase'] = pass_phrase
            self._config['options'] = options

        self.etag = None
        self.save_connection = save_connection
        if save_connection:
            self.connection = connection
        else:
            self.connection = None

    def template_id(self):
        """
        The template ID, MarkLogic's internal identifier.

        :return: The template ID.
        """
        return self._get_config_property('template-id')

    def template_name(self):
        """
        The template name.

        :return: The current template name.
        """
        return self._get_config_property('template-name')

    def set_template_name(self, value):
        """
        Set the template name.

        :param value: The new template name.

        :return: The Template object.
        """
        self._config['template-name'] = value
        return self

    def template_description(self):
        """
        The template description.

        :return: The current template description.
        """
        return self._get_config_property('template-description')

    def set_template_description(self, value):
        """
        Set the template description.

        :param value: The new template description.

        :return: The Template object.
        """
        self._config['template-description'] = value
        return self

    def template_version(self):
        """
        The template version.

        :return: The current template version.
        """
        return self._get_config_property('template-version')

    def key_type(self):
        """
        The key type.

        :return: The current key type.
        """
        return self._get_config_property('key-type')

    def set_key_type(self, value):
        """
        Set the key type.

        The key type must be `rsa`.
        """
        if value is not 'rsa':
            validate_custom("The key-type must be 'rsa'")
        self._config['key-type'] = value
        return self

    def key_length(self):
        """
        The key length.

        :return: The current key length.
        """
        if 'options' in self._config:
            if 'key-length' in self._config['options']:
                return self._config['options']['key-length']
        return None

    def set_key_length(self, value):
        """
        Set the key length.

        :param value: The new key length.

        :return: The Template object.
        """
        if 'options' in self._config:
            options = self._config['options']
        else:
            options = {}

        options['key-length'] = value
        self._config['options'] = options
        return self

    def pass_phrase(self):
        """
        The passphrase.

        :return: The current passphrase.
        """
        if 'options' in self._config:
            if 'pass-phrase' in self._config['options']:
                return self._config['options']['pass-phrase']
        return None

    def set_pass_phrase(self, value):
        """
        Set the passphrase.

        :param value: The new passphrase.

        :return: The Template object.
        """
        if 'options' in self._config:
            options = self._config['options']
        else:
            options = {}

        options['pass-phrase'] = value
        self._config['options'] = options
        return self

    def options(self):
        """
        The template options.

        The options are returned as a Python dictionary. Only the `key-length`
        and `pass-phrase` options are supported by MarkLogic at this time,
        but this method returns the entire dictionary.

        :return: The options dictionary.
        """
        return self._get_config_property('options')

    def set_options(self, value):
        """
        Set the template options.

        The options are stored in a Python dictionary. Only the `key-length`
        and `pass-phrase` options are supported by MarkLogic at this time,
        but this method allows you to set any dictionary of options you like.

        :param value: A dictionary of options.

        :return: The Template object.
        """
        self._config['options'] = value
        return self

    def req(self):
        """
        The certificate request.

        :return: The current certificate request.
        """
        return self._get_config_property('req')

    def set_req(self, value):
        """
        Set the certificate request.

        :param value: The certificate request.

        :return: The Template object.
        """
        self._config['req'] = assert_type(value, Request)
        return self

    def marshal(self):
        """
        Return a flat structure suitable for conversion to JSON or XML.

        :return: A hash of the keys in this object and their values, recursively.
        """
        struct = { }
        for key in self._config:
            if key == "req":
                struct[key] = self._config[key]._config
            else:
                struct[key] = self._config[key];
        return struct

    @classmethod
    def unmarshal(cls, config):
        """
        Construct a new Template from a flat structure. This method is
        principally used to construct an object from a Management API
        payload. The configuration passed in is largely assumed to be
        valid.

        :param: config: A hash of properties
        :return: A newly constructed User object with the specified properties.
        """
        result = Template("temp","temp", Request(organizationName="temp"))
        result._config = config

        if 'req' in result._config:
            result._config['req'] = Request.unmarshal(result._config['req'])

        return result

    def create(self, connection=None):
        """
        Creates the certificate template on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Template object
        """
        if connection == None:
            connection = self.connection

        uri = connection.uri("certificate-templates")
        struct = self.marshal()
        response = connection.post(uri, payload=struct)

        # All well and good, but we need to know what ID was assigned
        uri = "{0}://{1}:{2}{3}/properties" \
          .format(connection.protocol, connection.host,
                  connection.management_port,
                  response.headers['location'])

        response = connection.get(uri)

        if response.status_code == 200:
            result = Template.unmarshal(json.loads(response.text))
            self._config = result._config
        else:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def read(self, connection=None):
        """
        Loads the Template from the MarkLogic server. This will refresh
        the properties of the object.

        :param connection: The connection to a MarkLogic server

        :return: The Template object
        """
        if connection == None:
            connection = self.connection

        if self.template_id() is None:
            validate_custom("Cannot read an unsaved template")

        temp = Template.lookup(connection, self.template_id())

        if auth is None:
            return None
        else:
            self._config = auth._config
            return self

    def update(self, connection=None):
        """
        Updates the certificate template on the MarkLogic server.

        :param connection: The connection to a MarkLogic server
        :return: The Template object
        """
        if connection == None:
            connection = self.connection

        uri = connection.uri("certificate-templates", self.template_id())

        struct = self.marshal()
        del struct['template-version']
        del struct['template-id']

        response = connection.put(uri, payload=struct)
        return self

    def delete(self, connection=None):
        """
        Deletes the Template from the MarkLogic server.

        :param connection: The connection to a MarkLogic server

        :return: None
        """
        if connection == None:
            connection = self.connection

        uri = connection.uri("certificate-templates", self.template_id(),
                             properties=None)

        response = connection.delete(uri, etag=self.etag)
        return self

    # ============================================================

    def generate_template_certificate_authority(self, valid_for, connection=None):
        """
        Attempts to generate an template certificate authority.

        :param valid_for: The number of days that the template should be valid.

        :return: The Template object.
        """
        if connection == None:
            connection = self.connection

        struct = {
            'operation': 'generate-template-certificate-authority',
            'valid-for': assert_type(valid_for, int)
            }

        uri = connection.uri("certificate-templates", self.template_id(),
                             properties=None)

        response = connection.post(uri, payload=struct)

        if response.status_code != 201:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def generate_temporary_certificate(self, valid_for,
                                       common_name, dns_name, ip_addr,
                                       connection=None,
                                       if_necessary=True):
        """
        Attempts to generate a temporary certificate.

        If `if_necessary` is true, the server will only generate a new
        temporary certificate if it does not already have one for the
        specified server.

        :param valid_for: The number of days that the template should be valid.
        :param common_name: The common name for the certificate ("Example Corp")
        :param dns_name: The DNS name for the cert ("example.com")
        :param ip_addr: The IP address of the server
        :param if_necessary: Only generate the cert if it's necessary

        :return: The Template object.
        """
        if connection == None:
            connection = self.connection

        struct = {
            'operation': 'generate-temporary-certificate',
            'valid-for': assert_type(valid_for, int),
            'common-name': common_name,
            'dns-name': dns_name,
            'ip-addr': ip_addr,
            'if-necessary': 'true' if if_necessary else 'false'
            }

        uri = connection.uri("certificate-templates", self.template_id(),
                             properties=None)
        response = connection.post(uri, payload=struct)

        if response.status_code != 201:
            raise UnexpectedManagementAPIResponse(response.text)

        return self

    def get_certificate(self, common_name, dns_name=None, ip_addr=None,
                        connection=None):
        """
        Attempts to get the relevant certificate.

        :param common_name: The common name for the certificate ("Example Corp")
        :param dns_name: The DNS name for the cert ("example.com")
        :param ip_addr: The IP address of the server

        :return: The certificate or None if it isn't found.
        """
        if connection == None:
            connection = self.connection

        struct = {
            'operation': 'get-certificate',
            'common-name': common_name
            }

        if dns_name is not None:
            struct['dns-name'] = dns_name

        if ip-addr is not None:
            struct['ip-addr'] = ip_addr

        uri = connection.uri("certificate-templates", self.template_id(),
                             properties=None)
        response = connection.post(uri, payload=struct)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def get_certificates_for_template(self, connection=None):
        """
        Get a list of the certificates for this template.

        :return: The certificate list.
        """
        if connection == None:
            connection = self.connection

        struct = {
            'operation': 'get-certificates-for-template',
            }

        uri = connection.uri("certificate-templates", self.template_id(),
                             properties=None)

        response = connection.post(uri, payload=struct)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def get_pending_certificate_request(self, common_name,
                                        dns_name=None, ip_addr=None,
                                        connection=None):
        pass

    def insert_host_certificates(self, certs, pkeys, connection=None):
        pass

    def need_certificate(self, common_name, dns_name=None, ip_addr=None,
                         connection=None):
        pass

    def generate_certificate_request(self,
                                     common_name, dns_name=None, ip_addr=None,
                                     connection=None):
        pass

    def get_template_certificate_authority(self, connection=None):
        pass

    # ============================================================

    @classmethod
    def list(cls, connection, include_names=False):
        """
        List all the certificate templates.

        If `include_names` is `True`, then the values in the list will be
        structured values consisting of the template ID and the template
        name separated by a "|".

        :param connection: The connection to a MarkLogic server
        :param include_names: Indicates if structured names should be returned.

        :return: A list of certificate template IDs.
        """

        uri = connection.uri("certificate-templates")
        response = connection.get(uri)

        if response.status_code != 200:
            raise UnexpectedManagementAPIResponse(response.text)

        results = []
        json_doc = json.loads(response.text)

        for item in json_doc['certificate-templates-default-list']['list-items']['list-item']:
            if include_names:
                results.append("{0}|{1}".format(item['idref'], item['nameref']))
            else:
                results.append(item['idref'])
        return results

    @classmethod
    def lookup(cls, connection, tempid):
        """
        Look up an individual certificate template by template id.

        :param connection: The connection to the MarkLogic database
        :param tempid: The certificate template id

        :return: The Template object
        """
        uri = connection.uri("certificate-templates", tempid)
        response = connection.get(uri)

        if response.status_code == 200:
            result = Template.unmarshal(json.loads(response.text))
            return result
        else:
            return None
