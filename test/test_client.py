# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

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
# Norman Walsh      02/11/2016     Initial tests
#

import unittest
from marklogic.connection import Connection
from marklogic.client import Transactions, Documents, Eval, ClientUtils
from marklogic.exceptions import UnexpectedManagementAPIResponse
from requests.auth import HTTPDigestAuth
from test.resources import TestConnection as tc
from test.settings import DatabaseSettings as ds

class TestClient(unittest.TestCase):
    """
    Basic client API tests.
    """

    def test_doc_create_xml(self):
        """
        Create an XML document.
        """
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        docs = Documents(conn)

        docs.set_database("Documents")
        docs.set_content_type("application/xml")
        docs.set_uri("/path/hello.xml")

        docs.delete()

        r = docs.put("<doc>Hello world!</doc>")

        self.assertEqual(201, r.status_code)

        r = docs.delete()

        self.assertEqual(204, r.status_code)

    def test_doc_create_json(self):
        """
        Create a JSON document.
        """
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        docs = Documents(conn)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        r = docs.put({"message": "Hello World"})

        self.assertEqual(201, r.status_code)

        r = docs.delete()

        self.assertEqual(204, r.status_code)

    def test_tx_rollback(self):
        """
        Rollback a transaction.
        """
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        docs = Documents(conn)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        trans = Transactions(conn)
        trans.set_database("Documents")
        trans.create()
        txid = trans.txid()

        docs.set_txid(txid)

        r = docs.put({"message": "Hello World"})
        self.assertEqual(201, r.status_code)

        trans.rollback()

        docs.set_txid(None)
        r = docs.get()

        self.assertEqual(404, r.status_code)

    def test_tx_commit(self):
        """
        Commit a transaction.
        """
        conn = Connection(tc.hostname, HTTPDigestAuth(tc.admin, tc.password))
        docs = Documents(conn)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        trans = Transactions(conn)
        trans.set_database("Documents")
        trans.create()
        txid = trans.txid()

        docs.set_txid(txid)

        r = docs.put({"message": "Hello World"})
        self.assertEqual(201, r.status_code)

        trans.commit()

        docs.set_txid(None)
        r = docs.get()

        self.assertEqual(200, r.status_code)

        docs.delete()

if __name__ == "__main__":
    unittest.main()
