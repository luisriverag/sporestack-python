#!/bin/sh

set -e

nosetests -vx

python2 sporestack/cli.py 2>&1 | grep arguments
python3 sporestack/cli.py 2>&1 | grep arguments

python2 sporestack/cli.py options | grep "CENTS PER DAY"
python3 sporestack/cli.py options | grep "CENTS PER DAY"

python2 sporestack/cli.py -h
python3 sporestack/cli.py -h

echo Success
