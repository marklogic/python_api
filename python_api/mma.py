#!/usr/bin/python3

import sys
import re
import os
import json
import pwd
import logging
import argparse
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
from marklogic.models.connection import Connection
from marklogic.cli.template import Template

def main():
  cli = Template()
  argv = sys.argv
  script = argv[0]
  del(argv[0]) # trim off the script name
  try:
    command = argv[0]
    artifact = argv[1]
  except IndexError:
    print("Usage: {0} command artifact ...".format(script))
    sys.exit(1)

  # Hack for the server case
  if artifact in ['http','xdbc','odbc','webdav']:
    stype = artifact
    artifact = 'server'
    argv[1] = 'server'
    if argv[2] == 'server':
      del(argv[2])
    argv.append("--type")
    argv.append(stype)

  templ = cli.command_template(command)
  if templ is None:
    print("The command '{0}' is unrecognized".format(command))
    sys.exit(1)

  if artifact in templ:
    parser = templ[artifact]["parser"]
  else:
    print("The command '{0}' doesn't take '{1}' artifacts."
          .format(command,artifact))
    sys.exit(1)

  args = vars(parser.parse_args(argv))

  if args['debug']:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("marklogic").setLevel(logging.DEBUG)

  try:
    username, password = re.split(":", args['credentials'])
  except ValueError:
    print ("--credentials value must be 'user:password':",
           args['credentials'])
    sys.exit(1)

  host = args['host']
  conn = Connection(host, HTTPDigestAuth(username, password))

  # do it!
  templ[artifact]["code"](args, conn)

if __name__ == '__main__':
  main()
