import json
from marklogic.connection import Connection
from requests.auth import HTTPDigestAuth
from unittest import TestCase

class MLConfig(TestCase):
    def __init__(self, *args, **kwargs):
        super(MLConfig,self).__init__(*args, **kwargs)

        config = { "hostname": "localhost", \
                       "username": "admin", \
                       "password": "admin", \
                       "protocol": "http", \
                       "port": 8000, \
                       "management-port": 8002, \
                       "root": "manage", \
                       "version": "v2", \
                       "client-version": "v1" }
        try:
            data_file = open("mlconfig.json").read()
            data = json.loads(data_file)
            for key in data:
                config[key] = data[key]
        except FileNotFoundError:
            pass

        self.auth = HTTPDigestAuth(config["username"], config["password"])
        self.connection = Connection(config["hostname"], self.auth, \
                                         protocol=config["protocol"], \
                                         port=config["port"], \
                                         management_port=config["management-port"], \
                                         root=config["root"], \
                                         version=config["version"], \
                                         client_version=config["client-version"])
