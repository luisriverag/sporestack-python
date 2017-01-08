"""
Creates a 28 day Bitcoin Unlimited node in Dallas.

Doesn't work.
"""

from uuid import uuid4 as random_uuid
from time import sleep
import os

import pyqrcode
import sporestack

# 1 - 28
DAYS = 28

# 3 is DFW.
DCID = 3

# FreeBSD 11. Will need to change the startupscript if you adjust this.
OSID = 230

# 4GiB memory, 90GiB disk
FLAVOR=95

node_uuid = str(random_uuid())

ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

with open(ssh_key_path) as ssh_key_file:
    sshkey = ssh_key_file.read()

with open('bitcoinunlimited.sh') as startup_file:
    startupscript = startup_file.read()

# This is broken.
while False:
    node = sporestack.node(days=28,
                           sshkey=sshkey,
                           startupscript=startupscript,
                           unique=node_uuid,
                           flavor=FLAVOR,
                           osid=OSID,
                           dcid=DCID)
    if node.payment_status is False:
        amount = "{0:.8f}".format(node.satoshis *
                                  0.00000001)
        uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
        qr = pyqrcode.create(uri)
        print(qr.terminal())
        print(uri)
        print('Pay with Bitcoin. Resize your terminal if QR code is unclear.')
    else:
        print('Node being built...')
    if node.creation_status is True:
        break
    sleep(5)

banner = '''

UUID: {}
IPv6: {}
IPv4: {}
End of Life: {}

May take a few more moments to come online.

'''.format(node_uuid,
           node.ip6,
           node.ip4,
           node.end_of_life)

print(banner)
