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
# Norman Walsh      6 August 2015  Initial development
#

"""
A class to manage setup activities on the server.
"""

import json, logging, os, re, requests, shutil, socket, subprocess, sys, time
from http.client import BadStatusLine
from requests.packages.urllib3.exceptions import ProtocolError,ReadTimeoutError
from requests.exceptions import ConnectionError,ReadTimeout
from marklogic.cli.manager import Manager
from marklogic.models.user import User
from marklogic.models.host import Host
from marklogic.models.cluster import LocalCluster
from marklogic import MarkLogic

class MarkLogicManager(Manager):
    """
    The MarkLogicManager performs operations on the server (init, stop, etc.).
    """
    def __init__(self):
        self.logger = logging.getLogger("marklogic.cli")

    def start(self, args, config, connection):
      try:
        cmd = config[args['config']]['start']
      except KeyError:
        print("No start command in configuration file for section: {0}"
              .format(args['config']))
        sys.exit(1)

      status = self.status(args,config,connection,internal=True)
      if status == 'up':
        print("MarkLogic server on {0} appears to be {1}."
              .format(connection.host, status))
      else:
          args = cmd.split(" ")
          print("Starting {0}".format(args[0]))
          proc = subprocess.Popen(args)
          status = self.status(args,config,connection,internal=True)
          while status != 'up':
              time.sleep(2)
              status = self.status(args,config,connection,internal=True)

    def init(self, args, config, connection):
        status = self.status(args,config,connection,internal=True)
        if status == 'up':
            print("Cannot initialize a running host!")
            sys.exit(1)
        else:
            if connection.host == 'localhost':
                try:
                    data = config[args['config']]['datadir']
                    print("Clearing {0}...".format(data))
                    self._clear_directory(data)
                except KeyError:
                    pass
            else:
                self.logger.info("Skipping clear data directory; not localhost")
            self.start(args,config,connection)

        print("Initializing {0}...".format(connection.host))
        MarkLogic.instance_init(connection.host)
        MarkLogic.instance_admin(connection.host, args['realm'],
                                 connection.auth.username,
                                 connection.auth.password)

    def _clear_directory(self, data):
        if not os.path.isdir(data):
            print("Not a directory: {}".format(data))
            sys.exit(1)
        for name in os.listdir(data):
            path = os.path.join(data, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def status(self, args, config, connection, internal=False):
        if connection is None:
            host = "localhost"
        else:
            host = connection.host

        uri = "http://{0}:7997/".format(host)
        status = "down"

        try:
            self.logger.debug("Checking status of {0}".format(host))
            response = requests.get(uri, timeout=1)
            # If we got any sort of reply, even 500 for an uninitialized
            # server, we call that "up".
            status = "up"
        except TypeError:
            self.logger.debug("{0}: {1}".format(response.status_code,
                                           response.text))
            pass
        except BadStatusLine:
            self.logger.debug("{0}: {1}".format(response.status_code,
                                           response.text))
            pass
        except ProtocolError:
            self.logger.debug("{0}: {1}".format(response.status_code,
                                           response.text))
            pass
        except ReadTimeoutError:
            self.logger.debug("ReadTimeoutError error...")
            pass
        except ReadTimeout:
            self.logger.debug("ReadTimeout error...")
            pass
        except ConnectionError:
            self.logger.debug("Connection error...")
            pass

        if internal:
            return status
        else:
            print("MarkLogic server on {0} appears to be {1}."
                  .format(host, status))

    def restart(self, args, config, connection):
        status = self.status(args, config, connection, internal=True)
        if status == 'down':
            print("MarkLogic server on {0} appears to be {1}."
                  .format(connection.host, status))
        else:
            if 'cluster' in args:
                hostname = connection.host
                if hostname == 'localhost':
                    hostname = socket.gethostname()
                cluster = LocalCluster(connection=connection).read()
                print("Restarting cluster...")
                cluster.restart()
                # Make sure it's back up
                status = self.status(args,config,connection,internal=True)
                while status != 'up':
                    time.sleep(2)
                    status = self.status(args,config,connection,internal=True)
            else:
                hostname = connection.host
                if hostname == 'localhost':
                    hostname = socket.gethostname()
                host = Host(hostname,connection=connection).read()
                print("Restarting host...")
                host.restart()
                # Make sure it's back up
                status = self.status(args,config,connection,internal=True)
                while status != 'up':
                    time.sleep(2)
                    status = self.status(args,config,connection,internal=True)

    def stop(self, args, config, connection):
        status = self.status(args, config, connection, internal=True)
        if status == 'down':
            print("MarkLogic server on {0} appears to be {1}."
                  .format(connection.host, status))
        else:
            if 'cluster' in args:
                hostname = connection.host
                if hostname == 'localhost':
                    hostname = socket.gethostname()
                cluster = LocalCluster(connection=connection).read()
                print("Shutting down cluster...")
                cluster.shutdown()
                # Make sure it's all the way down
                status = self.status(args,config,connection,internal=True)
                while status != 'down':
                    time.sleep(2)
                    status = self.status(args,config,connection,internal=True)
            else:
                hostname = connection.host
                if hostname == 'localhost':
                    hostname = socket.gethostname()
                host = Host(hostname,connection=connection).read()

                if host.group_name() is None:
                    ml = MarkLogic(connection)
                    if len(ml.hosts()) == 1:
                        host = Host(ml.hosts()[0], connection=connection).read()
                    else:
                        print("Failed to identify host:",ml.hosts())
                        sys.exit(1)

                print("Shutting down host: " + host.host_name())
                host.shutdown()
                # Make sure it's all the way down
                status = self.status(args,config,connection,internal=True)
                while status != 'down':
                    time.sleep(2)
                    status = self.status(args,config,connection,internal=True)

            status = self.status(args,config,connection,internal=True)
            while status == 'up':
                time.sleep(2)
                status = self.status(args,config,connection,internal=True)

    def save(self, args, config, connection):
        try:
            arcdir = config[args['config']]['archivedir']
        except KeyError:
            print("No archivedir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        try:
            datadir = config[args['config']]['datadir']
        except KeyError:
            print("No datadir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        status = self.status(args,config,connection,internal=True)
        if status == 'up':
            self.stop(args,config,connection)

        arc = args['archive']
        if "/" in arc or "\\" in arc:
            print("You may not specify a path, only a name: {0}"
                  .format(arc))
            sys.exit(1)

        if arc.endswith(".gz"):
            arc = arc[:-3]
        if arc.endswith(".tar"):
            arc = arc[:-4]
        if not arcdir.endswith('/'):
            arcdir += "/"

        path = datadir.split('/')
        lastseg = path.pop()
        parent = "/".join(path)
        os.chdir(parent)

        archive = arcdir + arc

        try:
            os.unlink(archive+".tar.gz")
        except FileNotFoundError:
            pass

        try:
            os.unlink(archive+".tar")
        except FileNotFoundError:
            pass

        print("Saving {0} to {1}.tar.gz".format(datadir,archive))
        subprocess.call(["/bin/tar", "-cf", archive+".tar", lastseg])
        subprocess.call(["/bin/gzip", archive+".tar"])

        if status == 'up':
            self.start(args,config,connection)

    def switch(self, args, config, connection):
        try:
            arcdir = config[args['config']]['archivedir']
        except KeyError:
            print("No archivedir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        try:
            datadir = config[args['config']]['datadir']
        except KeyError:
            print("No datadir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        status = self.status(args,config,connection,internal=True)
        if status == 'up':
            self.stop(args,config,connection)

        arc = args['archive']
        if "/" in arc or "\\" in arc:
            print("You may not specify a path, only a name: {0}"
                  .format(arc))
            sys.exit(1)

        if arc.endswith(".gz"):
            arc = arc[:-3]
        if arc.endswith(".tar"):
            arc = arc[:-4]
        if not arcdir.endswith('/'):
            arcdir += "/"

        path = datadir.split('/')
        lastseg = path.pop()
        parent = "/".join(path)
        os.chdir(parent)

        archive = arcdir + arc
        if not os.path.exists(archive + '.tar.gz'):
            print("No such archive: {0}.tar.gz".format(archive))
            sys.exit(1)

        print("Switching {0} to {1}.tar.gz".format(datadir,archive))
        self._clear_directory(datadir)
        subprocess.call(["/bin/tar", "-zxf", archive+".tar.gz", lastseg])

        if status == 'up':
            self.start(args,config,connection)

    def clear(self, args, config, connection):
        try:
            datadir = config[args['config']]['datadir']
        except KeyError:
            print("No datadir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        status = self.status(args,config,connection,internal=True)
        if status == 'up':
            self.stop(args,config,connection)

        print("Clearing {0}".format(datadir))
        shutil.rmtree(datadir)
        os.mkdir(datadir)

        if status == 'up':
            self.start(args,config,connection)

    def log(self, args, config, connection):
        try:
            datadir = config[args['config']]['datadir']
        except KeyError:
            print("No datadir in configuration file for section: {0}"
                  .format(args['config']))
            sys.exit(1)

        if not datadir.endswith('/'):
            datadir += "/"

        logfile = args['logfile']
        if "/" in logfile or "\\" in logfile:
            print("You may not specify a path, only a name: {0}"
                  .format(logfile))
            sys.exit(1)

        status = self.status(args,config,connection,internal=True)
        try:
            if status == 'up':
                subprocess.call(['/usr/bin/tail', '-f', datadir + "Logs/" + logfile])
            else:
                subprocess.call(['/usr/bin/tail', datadir + "Logs/" + logfile])
        except KeyboardInterrupt:
            pass

    def debug(self, args, config, connection):
        section = config[args['config']]
        if 'diagnostic-events' in section:
            events = []
            devents = section['diagnostic-events'].strip()
            if devents != '':
                for event in devents.split(","):
                    events.append(event.strip())
        else:
            events = []

        ml = MarkLogic(connection)
        group = ml.group(args['group'])

        group.set_events(events)

        if len(events) == 0:
            group.set_events_activated(False)
        else:
            group.set_events_activated(True)

        group.update()
