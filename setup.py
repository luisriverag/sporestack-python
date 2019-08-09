#!/usr/bin/env python

from setuptools import setup

# Not sure how necessary this is. Would be nice to just
# import .sporestackv2.__version__
VERSION = None
with open('sporestackv2/version.py') as f:
    for line in f:
        if line.startswith('__version__'):
            VERSION = line.replace("'", '').split('=')[1].strip()
            break
if VERSION is None:
    raise ValueError('__version__ not found in __init__.py')

DOWNLOAD_URL = 'https://github.com/sporestack/sporestack-python/tarball/{}'

DESCRIPTION = 'SporeStack.com library and client. Launch servers with Bitcoin.'
KEYWORDS = ['bitcoin', 'bitcoincash', 'bitcoinsv', 'servers', 'infrastructure',
            'vps', 'virtual private server']

setup(
    python_requires='>=3.3',
    name='sporestack',
    version=VERSION,
    author='SporeStack',
    author_email='admin@sporestack.com',
    description=DESCRIPTION,
    keywords=KEYWORDS,
    license='Unlicense',
    url='https://sporestack.com/',
    download_url=DOWNLOAD_URL.format(VERSION),
    packages=['sporestackv2'],
    install_requires=[
        'pyqrcode',
        'requests[socks]>=2.22.0',
        'aaargh',
        'walkingliberty',
        'paramiko',
        'sshpubkeys'
    ],
    entry_points={
        'console_scripts': [
            'sporestackv2 = sporestackv2.client:main'
        ]
    }
)
