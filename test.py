"""
Just some basic tests.

Kinda broken.
"""

from uuid import uuid4 as random_uuid
import os

import sporestack

script = """#!/bin/sh
            date > /date
         """
new_uuid = str(random_uuid())

ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

with open(ssh_key_path) as ssh_key_file:
    sshkey = ssh_key_file.read()

for unique in ['3b69d7c9-ad4d-4d31-b04e-b224f02de4d4',
               new_uuid]:
    node = sporestack.node(days=1,
                           sshkey=sshkey,
                           unique=unique,
                           cloudinit=script,
                           startupscript=script)
    print('Payment status: ' + str(node.payment_status))
    print('Creation status: ' + str(node.creation_status))
    print(node.address)
    print(node.satoshis)
    print(node.ip6)
    print(node.ip4)
