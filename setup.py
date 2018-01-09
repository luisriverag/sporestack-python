#!/usr/bin/env python

from setuptools import setup

try:
    with open('sporestack/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                VERSION = line.replace("'", '').split('=')[1].strip()
                break
except:
    print('Version not set.')

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

DESCRIPTION = 'SporeStack.com library and client. Launch servers with Bitcoin.'

setup(
    name='sporestack',
    version=VERSION,
    author='Teran McKinney',
    author_email='sega01@go-beyond.org',
    description=DESCRIPTION,
    keywords=['bitcoin', 'bitcoincash', 'servers', 'infrastructure', 'vps', 'ephemeral'],
    license='Unlicense',
    url='https://sporestack.com/',
    download_url=DOWNLOAD_URL.format(VERSION),
    packages=['sporestack'],
    install_requires=[
        'pyqrcode'
    ],
    entry_points={
        'console_scripts': [
            'sporestack = sporestack.cli:main'
        ]
    }
)
