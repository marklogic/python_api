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
# James Fuller      12 Jun 2016    Initial development
#
import json
from mlconfig import MLConfig
from marklogic.models.amp import Amp
from marklogic.exceptions import UnexpectedManagementAPIResponse
from marklogic.models.cluster import LocalCluster,ForeignCluster
from marklogic.models import Forest,Database,Server,Host

class TestView(MLConfig):

    def test__connection_view_uri(self):
        connection = self.connection
        viewuri = connection.view_uri(version="v2",port=8002,path="forests", protocol="http",view="status")
        assert viewuri == "http://localhost:8002/manage/v2/forests?view=status"

    def test__connection_status_view(self):
        connection = self.connection
        viewuri = connection.view_uri(version="v2",port=8002,path="forests", protocol="http",view="status")
        response = connection.get(viewuri, accept="application/json")
        assert response.status_code == 200
        assert response.json()["forest-status-list"]["meta"]["uri"] == "/manage/v2/forests?view=status"
        assert response.json()["forest-status-list"]["status-list-summary"]["total-forests"]

    def test__connection_metrics_view(self):
        connection = self.connection
        viewuri = connection.view_uri(version="v2",port=8002,path="forests", protocol="http",view="metrics")
        response = connection.get(viewuri, accept="application/json")
        assert response.status_code == 200
        assert response.json()["forest-metrics-list"]["meta"]["uri"] == "/manage/v2/forests?view=metrics"
        assert response.json()["forest-metrics-list"]["metrics-relations"]["forest-metrics-list"]["metrics"][0]["active-fragment-count"]["name"] == "active-fragment-count"
    def test__model_get_all_forest_status(self):
        connection = self.connection
        response = Forest.get_status_view(connection)
        assert response.status_code == 200
        assert response.json()["forest-status-list"]["status-list-summary"]["total-forests"]

    def test__model_get_all_forest_metrics(self):
        connection = self.connection
        response = Forest.get_metric_view(connection,period="hour",summary="false",detail="false")
        assert response.status_code == 200
        #assert response.json()["forest-metrics-list"]["meta"]["uri"] == "/manage/v2/forests?view=metrics&detail=false&period=hour&summary=false"
        assert response.json()["forest-metrics-list"]["metric-properties"]["period"] == "hour"
        assert response.json()["forest-metrics-list"]["metric-properties"]["summary"] == "false"
        assert response.json()["forest-metrics-list"]["metric-properties"]["detail"] == "false"
        assert response.json()["forest-metrics-list"]["metrics-relations"]["forest-metrics-list"]["metrics"][0]["active-fragment-count"]["name"] == "active-fragment-count"

    def test__model_get_specific_forest_status(self):
        connection = self.connection
        response = Forest.get_status_view(connection,name="Documents")
        assert response.status_code == 200
        assert response.json()["forest-status"]["name"]

    def test__model_get_specific_database_status(self):
        connection = self.connection
        response = Database.get_status_view(connection,"Documents")
        assert response.status_code == 200
        assert response.json()["database-status"]

    # def test__model_get_specific_group_status(self):
    #     connection = self.connection
    #     response = Group.get_status_view(connection,"Default")
    #     assert response.status_code == 200
    #     assert response.json()["group-status"]

    def test__model_get_server_status(self):
        connection = self.connection
        response = Server.get_status_view(connection)
        assert response.status_code == 200
        assert response.json()["server-status-list"]

    def test__model_get_specific_server_status(self):
        connection = self.connection
        response = Server.get_status_view(connection,"Manage","Default")
        assert response.status_code == 200
        assert response.json()["server-status"]

    def test__model_get_host_status(self):
        connection = self.connection
        response = Host.get_status_view(connection)
        assert response.status_code == 200
        assert response.json()["host-status-list"]

    def test__model_get_specific_host_status(self):
        connection = self.connection
        response = Host.get_status_view(connection,"127.0.0.1")
        assert response.status_code == 200
        assert response.json()["host-status"]

    def test__model_get_local_cluster_status(self):
        connection = self.connection
        response = LocalCluster.get_status_view(connection)
        assert response.status_code == 200
        assert response.json()["local-cluster-status"]

    # def test__model_get_specific_foreign_cluster_status(self):
    #     connection = self.connection
    #     response = ForeignCluster.get_status_view(connection)
    #     assert response.status_code == 200
    #     assert response.json()["local-cluster-status"]
