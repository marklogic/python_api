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

"""
Support the CMA V3 endpoint
"""

import json, logging, sys
import requests
from marklogic.exceptions import *

class CMA:
    """
    CMA class provides methods to generate and apply application configuration
    """

    _cma_version = "v3"
    _min_support_version = 9.0-5

    def __init__(self, connection, params={}, scenario=None, format="json"):
        self.connection = connection
        self.params = params
        self.scenario = scenario
        self.format = format
        self.logger = logging.getLogger("marklogic.client.cma")

    @property
    def scenario(self):
        """
        Scenario property for generate config(ex. ha-local)
        :return:scenario as string
        """
        return self.__scenario

    @scenario.setter
    def scenario(self, scenario):
        self.__scenario = scenario

    #
    @property
    def params(self):
        """
        Params for generate and apply config
        ref: http://docs.marklogic.com/REST/configuration-management-api
        :return:params as dict
        """
        return self.__params

    @params.setter
    def params(self, params):
        if isinstance(params, dict):
            self.__params = params
        else:
            raise Exception("Params should be a dict")

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, format):
        self.__format = format

    def generate_config(self):
        """
        Generate configuration for different scenarios
        :return configuration as string(format : xml/json) or binary(format:zip)
        """

        cma_url = "http://{0}:{1}/{2}/{3}" \
            .format(self.connection.host, self.connection.management_port, self.connection.root, self._cma_version)

        cma_url = (cma_url + "?format={}").format(self.format)

        if self.scenario:
            cma_url = (cma_url+"&scenario={}").format(self.scenario)
        if self.params:
            cma_url = (cma_url+"&params={}").format(json.dumps(self.params))

        print(cma_url)

        response = requests.get(cma_url, auth=self.connection.auth)

        if response.status_code == 404:
            return None
        elif response.status_code == 200:
            return response.text
        else:
            raise UnexpectedAPIResponse(response.text)

    def apply_config(self, config, content_type):
        """
        Applies the specified configuration on MarkLogic
        :param config: configuration to be applied as string
        :param content_type: application/json or application/xml
        :return response object
        """
        cma_url = "http://{0}:{1}/{2}/{3}" \
            .format(self.connection.host, self.connection.management_port, self.connection.root, self._cma_version)
        if self.params:
            cma_url = (cma_url+"&params={}").format(self.params)
        response = requests.post(cma_url, data=config, auth=self.connection.auth,
                                headers={'content-type': content_type})
        if response.status_code > 299:
            raise UnexpectedAPIResponse(response.text)
        return response
