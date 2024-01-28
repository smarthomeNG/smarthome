#!/bin/bash

# get directory where this script is stored
SOURCE=${BASH_SOURCE[0]}
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

# change to BASE dir, because tests must br run from BASE dir
cd $DIR
cd ..
SHNG_BASEDIR=`pwd`

# needs to be called from BASE with ``tests/run.sh``
# where BASE normally equals to ``/usr/local/smarthome``
# ``python3 -m unittest`` equals to ``python3 -m unittest discover``

clear
python3 -m unittest

