#!/usr/bin/env python

from setuptools import setup

VERSION = '0.6.8'

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

DESCRIPTION = 'SporeStack.com library and client. Launch servers with Bitcoin.'

setup(
    name='sporestack',
    version=VERSION,
    author='Teran McKinney',
    author_email='sega01@go-beyond.org',
    description=DESCRIPTION,
    keywords=['bitcoin', 'servers', 'infrastructure', 'vps', 'ephemeral'],
    license='Unlicense',
    url='https://sporestack.com/',
    download_url=DOWNLOAD_URL.format(VERSION),
    packages=['sporestack'],
    install_requires=[
        'pyyaml',
        'pyqrcode'
    ],
    entry_points={
        'console_scripts': [
            'sporestack = sporestack.cli:main',
            'nodemeup = sporestack.cli:nodemeup'
        ]
    }
)
