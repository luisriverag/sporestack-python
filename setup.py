#!/usr/bin/env python

from setuptools import setup

VERSION = None
with open('sporestack/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            VERSION = line.replace("'", '').split('=')[1].strip()
            break
if VERSION is None:
        raise ValueError('__version__ not found in __init__.py')

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

DESCRIPTION = 'SporeStack.com library and client. Launch servers with Bitcoin.'

setup(
    python_requires='>=3.3',
    name='sporestack',
    version=VERSION,
    author='SporeStack',
    author_email='admin@sporestack.com',
    description=DESCRIPTION,
    keywords=['bitcoin', 'bitcoincash', 'servers', 'infrastructure', 'vps', 'ephemeral'],
    license='Unlicense',
    url='https://sporestack.com/',
    download_url=DOWNLOAD_URL.format(VERSION),
    packages=['sporestack', 'sporestackv2'],
    install_requires=[
        'pyqrcode',
        'requests',
        'aaargh',
        'walkingliberty',
        'paramiko',
        'sshpubkeys'
    ],
    entry_points={
        'console_scripts': [
            'sporestack = sporestack.cli:main',
            'sporestackv2 = sporestackv2.client:main'
        ]
    }
)
