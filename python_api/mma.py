#!/usr/bin/python3

import argparse, configparser, json, logging, os, pwd, re, shlex, sys
from requests.auth import HTTPDigestAuth
from marklogic import MarkLogic
import marklogic.cli.manager
from marklogic.connection import Connection
from marklogic.cli.template import Template

def main():
  try:
    inifile = "{0}/.marklogic.ini".format(os.environ['HOME'])
  except KeyError:
    print("Configuration problem, no HOME in environment?")
    sys.exit(1)

  config = configparser.ConfigParser()
  config.read(inifile)

  argv = sys.argv
  script = argv[0]
  del(argv[0]) # trim off the script name
  run(config, argv)

def run(config, argv):
  cli = Template()
  command = None
  artifact = None

  try:
    command = argv[0]
  except IndexError:
    print("Usage: {0} command artifact ...".format(script))
    sys.exit(1)

  empty_artifact_commands = {'start','status', 'stop', 'init',
                             'save', 'switch', 'clear', 'log'}
  try:
    artifact = argv[1]
    if artifact.startswith("-"):
      artifact = None
  except IndexError:
    if command in empty_artifact_commands:
      pass
    else:
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

  # Hack for the stop case
  if command == 'stop' and artifact is None:
    argv.append('host')
    artifact = 'host'

  templ = cli.command_template(command)
  if templ is None:
    print("The command '{0}' is unrecognized".format(command))
    sys.exit(1)

  if artifact is None:
    if 'parser' in templ:
      parser = templ['parser']
    else:
      print("The command '{0}' isn't recognized."
            .format(command,artifact))
      sys.exit(1)
  else:
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

  host = args['hostname']
  conn = Connection(host, HTTPDigestAuth(username, password))

  # do it!
  if command == 'run':
    process_script(config, args['script'])
  else:
    if artifact is None:
      templ["code"](args, config, conn)
    else:
      templ[artifact]["code"](args, config, conn)

def process_script(config, scriptfn):
  print("Running", scriptfn)
  script = open(scriptfn, 'r')
  command = ""
  for line in script:
    line = line.strip()
    command = command + line
    if command.endswith("\\"):
      command = command[:-1]
    else:
      command = command.strip()
      #print(shlex.split(command))
      run(config, shlex.split(command))
      command = ""

  if command != "":
    print("Error: premature end of file on {0}".format(scriptfn))
    sys.exit(1)

if __name__ == '__main__':
  main()
