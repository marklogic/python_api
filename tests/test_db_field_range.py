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
# Paul Hoehne       03/05/2015     Initial development
#

from mlconfig import MLConfig
from marklogic.models.database.index import FieldRangeIndex
from marklogic.models.database import Database
from marklogic.models.database.field import PathField, RootField, FieldPath
from marklogic.models.database.field import IncludedElement, ExcludedElement

class TestDbFieldRange(MLConfig):
    def test_create_field(self):
        db = Database("testdb")

        assert 'field' not in db._config

        field = PathField("invoice-id", FieldPath("bill:invoice-id", 1))
        field.add_field_path(FieldPath("inv:id", 1))

        result = db.add_field(field)
        assert 'field' in  db._config
        assert result == db

        assert 1 == len(db._config['field'])

        field = db.fields()[0]
        assert "invoice-id" == field.field_name()

        field = db.fields()[0]
        assert 2 == len(field.field_paths())

        assert "bill:invoice-id" == field.field_paths()[0].path()
        assert 1 == field.field_paths()[0].weight()

    def test_include_references(self):
        field = RootField("invoice-id", \
                              includes=[IncludedElement("http://foo.bar.com/invoice", "id")])

        assert 1 == len(field.included_elements())
        assert "http://foo.bar.com/invoice" == field.included_elements()[0].namespace_uri()
        assert "id" == field.included_elements()[0].localname()

    def test_exclude_references(self):
        field = RootField("invoice-id", \
                              excludes=[ExcludedElement("http://foo.bar.com/invoice", "id")])

        assert 1 == len(field.excluded_elements())
        assert "http://foo.bar.com/invoice" == field.excluded_elements()[0].namespace_uri()
        assert"id" == field.excluded_elements()[0].localname()


    def test_create_element_reference(self):
        element_reference = IncludedElement("http://foo.bar.com/invoice", "id")

        assert "http://foo.bar.com/invoice" == element_reference.namespace_uri()
        assert "id" == element_reference.localname()

        element_reference = IncludedElement("http://foo.bar.com/invoice",
                                            "id", attribute_localname="foo")

        assert "foo" == element_reference.attribute_localname()

        element_reference = IncludedElement("http://foo.bar.com/invoice", "id",
                            attribute_namespace_uri="http://foo.bar.com/billing",
                            attribute_localname="bill")

        assert "http://foo.bar.com/billing" == element_reference.attribute_namespace_uri()

        element_reference = ExcludedElement("http://foo.bar.com/invoice", "id")

        assert "http://foo.bar.com/invoice" == element_reference.namespace_uri()
        assert "id" == element_reference.localname()

        element_reference = ExcludedElement("http://foo.bar.com/invoice",
                                            "id", attribute_localname="foo")

        assert "foo" == element_reference.attribute_localname()

        element_reference = ExcludedElement("http://foo.bar.com/invoice", "id",
                            attribute_namespace_uri="http://foo.bar.com/billing",
                            attribute_localname="bill")

        assert "http://foo.bar.com/billing" == element_reference.attribute_namespace_uri()

    #
    # {
    #   "scalar-type": "int",
    #   "collation": "",
    #   "field-name": "test-one",
    #   "range-value-positions": false,
    #   "invalid-values": "reject"
    # }
    #
    def test_create_range_field(self):
        db = Database("foo")

        field = RootField("invoice-id", False)
        db.add_field(field)

        range_field = FieldRangeIndex("int", "invoice-id")
        db.add_index(range_field)

        index = db.field_range_indexes()[0]
        assert "invoice-id" == index.field_name()
        assert "int" == index.scalar_type()

        indexes = db.field_range_indexes()
        assert 1 == len(indexes)
