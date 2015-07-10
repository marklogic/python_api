# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

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
# Paul Hoehne       03/03/2015     Initial development
# Norman Walsh      07/10/2015     Hacked at it
#

import os
import requests
import zipfile
import platform
import shutil
import subprocess
import logging


"""
These are assorted tools to help the end user.  The goal is to provide
a simple set of scripting interfaces.
"""

class MLCPLoader():
    """
    This class will execute the content pump to load data.
    """
    def __init__(self):
        pass

    def load(self, conn):
        pass

    def clear_directory(self):
        if os.path.isdir(".mlcp"):
            shutil.rmtree(".mlcp")

    def download_mlcp(self):
        os.mkdir(".mlcp")
        mlcp_url = "http://developer.marklogic.com/download/binaries/mlcp/mlcp-Hadoop2-1.3-1-bin.zip"
        archive_path = os.path.join(".mlcp", "mlcp.zip")
        chunk_size = 16 * 1024

        response = requests.get(mlcp_url, stream=True)
        with open(archive_path, "wb") as bin_file:
            for chunk in response.iter_content(chunk_size):
                bin_file.write(chunk)

        archive = zipfile.ZipFile(archive_path)
        archive.extractall(os.path.join(".mlcp"))
        for filename in os.listdir(".mlcp"):
            if filename.find("Hadoop") > -1:
                os.rename(os.path.join(".mlcp", filename), os.path.join(".mlcp", "mlcp"))

    def load_directory(self, conn, database, data_directory, collections=None, prefix=''):
        mlcp_path = self.mlcp_path()
        if not mlcp_path:
            which_script = "mlcp.sh"
            if platform.system() == "Windows":
                which_script = "mlcp.bat"

            mlcp_path = os.path.join(".mlcp", "mlcp", "bin", which_script)

            if not os.path.exists(mlcp_path):
                self.download_mlcp()

        if platform.system() != "Windows":
            subprocess.call(["chmod", "+x", mlcp_path])

        if collections:
            collections_command = "-output_collections \"{0}\"".format(",".join(collections))
        else:
            collections_command = ''

        command_line = "{0} import -username {1} -password {2} -host {3} -port {4} -database {5} {6} " \
                       "-input_file_path {7} -output_uri_replace \"{8},'{9}'\""

        full_path = os.path.abspath(data_directory)
        if platform.system() == "Windows":
            full_path = "/" + full_path.replace("\\", "/")
        run_line = command_line.format(mlcp_path, conn.auth.username, conn.auth.password, conn.host,
                                       conn.port, database.database_name(), collections_command,
                                       full_path, full_path, prefix)
        with os.popen(run_line) as in_file:
            for line in in_file:
                print(line.rstrip())

    def mlcp_installed(self):
        paths = os.environ["PATH"].split(os.pathsep)
        return True in [t.endswith("mlcp/bin") or t.endswith("mlcp\\bin") for t in paths]

    def mlcp_path(self):
        if platform.system() == "Windows":
            for path in os.environ["PATH"].split(os.pathsep):
                full_path = os.path.abspath(os.path.join(path, "mlcp.bat"))
                if os.path.exists(full_path):
                    return full_path
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                full_path = os.path.abspath(os.path.join(path, "mlcp.sh"))
                if os.path.exists(full_path):
                    return full_path
        return None


class Watcher():
    """
    Watcher will observe a directory and all the files in the director
    or its descendants.  If any change, it should upload the file to
    the appropriate database.
    """
    def __init__(self):
        pass

    def watch(self, conn, directory):
        pass
