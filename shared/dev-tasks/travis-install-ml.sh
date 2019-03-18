#!/bin/bash

# runs command from parameters and exits with the eoror code of the command
# if it fails
function successOrExit {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "$1 exited with error: $status"
        exit $status
    fi
}

test $1 && arg1=$1
if [[ $arg1 = 'release' ]]; then
  fname=marklogic.rpm
  ver="9.0-8.2"
  url="$MLRELEASE/MarkLogic-$ver.x86_64.rpm"

  echo "********* Downloading MarkLogic $ver"

  status=$(curl -k --head --write-out %{http_code} --silent --output /dev/null $url)
  if [[ $status = 200 ]]; then
    successOrExit curl -k -o ./$fname $url

    fname=$(pwd)/$fname

    sudo apt-get update
    sudo apt-get install wajig alien rpm lsb-base dpkg-dev debhelper build-essential
    (cd /etc && sudo ln -s default sysconfig)
    sudo wajig rpminstall $fname

    echo "********* MarkLogic $ver installed"
  else
    echo "CANNOT DOWNLOAD: status = $status"
    exit 1
  fi
else
  # FIXME: TBD.

  echo "Cannot download nightlies."
  exit 1
fi
