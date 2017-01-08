#!/usr/bin/env python

from setuptools import setup

VERSION = '0.1.1'

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

setup(
    name='sporestack',
    version=VERSION,
    author='Teran McKinney',
    author_email='sega01@go-beyond.org',
    description='Create servers for Bitcoin. sporestack.com library.',
    keywords=['bitcoin', 'servers', 'infrastructure'],
    license='Unlicense',
    url='http://sporestack.com/',
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
            'nodemeup = sporestack.nodemeup:fakemain'
        ]
    }
)
