# -*- coding: utf-8 -*-
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
# Paul Hoehne       03/25/2015     Initial development
# Paul Hoehne       03/26/2015     Adding dynamic lookup of host name
#

from mlconfig import MLConfig
from marklogic.models import Database, Host, Forest
from marklogic.exceptions import UnexpectedManagementAPIResponse

class TestDbDatabase(MLConfig):
    """
    Basic creation test function.

    """

    def test_simple_create(self):
        """TODO: The hostname should come from the server's hostname

        Test the basic create function. Creates a database and then
        check to see that it exists by getting the database
        configuration from the server. It then destroys the database.

        :return: None

        """
        hosts = Host.list(self.connection)
        db = Database("test-db", hosts[0])

        db.create(self.connection)

        validate_db = Database.lookup(self.connection, "test-db")
        try:
            assert validate_db is not None
            assert 'test-db' == validate_db.database_name()

        finally:
            validate_db.delete(connection=self.connection)
            validate_db = Database.lookup(self.connection, "test-db")
            assert validate_db is None

    def test_no_database_found(self):
        db = Database.lookup(self.connection, "No-Such-Database")

        assert db is None

    def test_list_databases(self):
        db_names = Database.list(self.connection)

        assert len(db_names) > 4

        assert "Modules" in db_names
        assert "Documents" in db_names

    def test_create_simple_forests(self):
        """
        Test the following scenario:

        The database is given the names of two forests.
        It should then create the two named forests.

        """
        hosts = Host.list(self.connection)
        db = Database("simple-forest-create-test-db", hosts[0],
                      connection=self.connection)

        db.set_forest_names(["simple-forest-create-forest1",
                             "simple-forest-create-forest2"])

        db.create()

        db = Database.lookup(self.connection, "simple-forest-create-test-db")
        try:
            assert 2 == len(db.forest_names())
            assert "simple-forest-create-forest1" in db.forest_names()
            assert "simple-forest-create-forest2" in db.forest_names()
        finally:
            db.delete(connection=self.connection)

    def test_create_single_detailed_forest(self):
        """
        Test the following scenario:

        The database is given a forest object.  It should create a forest with
        the given name.  That forest should match the features of the datailed
        forest.

        """

        hosts = Host.list(self.connection)
        db = Database("detailed-forest-create-test-db", hosts[0])

        forest = Forest("detailed-forest-create-forest1", host=hosts[0])
        forest.set_large_data_directory("")

        db.set_forest_names([forest.forest_name()])

        db.create(self.connection)

        forest = Forest.lookup(self.connection, "detailed-forest-create-forest1")

        try:
            assert "detailed-forest-create-forest1" == forest.forest_name()
            #this isn't in the properties...oddly.
            #self.assertEqual(ds.large_data_directory, forest.large_data_directory())
        finally:
            db.delete(connection=self.connection)
