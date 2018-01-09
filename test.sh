#!/bin/sh

set -e

nosetests-2.7

nosetests3

python2 sporestack/cli.py 2>&1 | grep arguments
python3 sporestack/cli.py 2>&1 | grep arguments

python2 sporestack/cli.py options | grep SATOSHIS
python3 sporestack/cli.py options | grep SATOSHIS

python2 sporestack/cli.py -h
python3 sporestack/cli.py -h

echo Success
