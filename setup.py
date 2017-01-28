#!/usr/bin/env python

from setuptools import setup

VERSION = '0.3.5'

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

setup(
    name='sporestack',
    version=VERSION,
    author='Teran McKinney',
    author_email='sega01@go-beyond.org',
    description='SporeStack.com library and client.',
    keywords=['bitcoin', 'servers', 'infrastructure'],
    license='Unlicense',
    url='https://sporestack.com/',
    download_url=DOWNLOAD_URL.format(VERSION),
    packages=['sporestack'],
    setup_requires=[
        'flake8'
    ],
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
