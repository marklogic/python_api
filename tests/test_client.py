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

from mlconfig import MLConfig
from marklogic.models import Host
from marklogic.client import Transactions, Documents, ClientUtils
from marklogic.exceptions import UnexpectedManagementAPIResponse

class TestClient(MLConfig):
    """
    Basic client API tests.
    """
    def test_doc_create_xml(self):
        """
        Create an XML document.
        """
        docs = Documents(self.connection)

        docs.set_database("Documents")
        docs.set_content_type("application/xml")
        docs.set_uri("/path/hello.xml")

        docs.delete()

        resp = docs.put("<doc>Hello world!</doc>")

        assert 201 == resp.status_code

        resp = docs.delete()

        assert 204 == resp.status_code

    def test_doc_create_json(self):
        """
        Create a JSON document.
        """
        docs = Documents(self.connection)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        resp = docs.put({"message": "Hello World"})

        assert 201 == resp.status_code

        resp = docs.delete()

        assert 204 == resp.status_code

    def test_tx_rollback(self):
        """
        Rollback a transaction.
        """
        docs = Documents(self.connection)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        trans = Transactions(self.connection)
        trans.set_database("Documents")
        trans.create()
        txid = trans.txid()

        docs.set_txid(txid)

        resp = docs.put({"message": "Hello World"})
        assert 201 == resp.status_code

        trans.rollback()

        docs.set_txid(None)

        resp = docs.get()

        assert 404 == resp.status_code

    def test_tx_commit(self):
        """
        Commit a transaction.
        """
        docs = Documents(self.connection)

        docs.set_database("Documents")
        docs.set_content_type("application/json")
        docs.set_uri("/path/hello.json")

        docs.delete()

        trans = Transactions(self.connection)
        trans.set_database("Documents")
        trans.create()
        txid = trans.txid()

        docs.set_txid(txid)

        resp = docs.put({"message": "Hello World"})
        assert 201 == resp.status_code

        trans.commit()

        docs.set_txid(None)
        resp = docs.get()

        assert 200 == resp.status_code

        docs.delete()
