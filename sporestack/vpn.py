"""
Build a VPN server

In progress!

Already out of date for help.
"""

import argparse
from uuid import uuid4 as random_uuid
from time import sleep
import os
from socket import create_connection

import pyqrcode
import sporestack

node_uuid = str(random_uuid())

ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

with open(ssh_key_path) as ssh_key_file:
    sshkey = ssh_key_file.read()

with open('vpn.sh') as startup_file:
    startupscript = startup_file.read()

parser = argparse.ArgumentParser()

parser.add_argument('--dcid', help='Datacenter ID '
                                   '3: Dallas, 2: Chicago, '
                                   '12: San Jose, 5: Los Angeles, '
                                   '6: Atlanta, 1: New Jersey, '
                                   '39: Miami, 4: Seattle',
                                   type=int)

args = parser.parse_args()


while True:
    node = sporestack.node(days=1,
                           sshkey=sshkey,
                           unique=node_uuid,
                           startupscript=startupscript,
                           osid=230,
                           dcid=args.dcid)
    if node.payment_status is False:
        amount = "{0:.8f}".format(node.satoshis *
                                  0.00000001)
        uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
        qr = pyqrcode.create(uri)
        print(qr.terminal())
        print(node_uuid)
        print(uri)
        print('Pay with Bitcoin. Resize your terminal if QR code is unclear.')
    else:
        print('Node being built...')
    if node.creation_status is True:
        break
    sleep(5)

print('Waiting for node to come online.')
ipaddress = None
while True:
    for ip in [node.ip6, node.ip4]:
        try:
            socket = create_connection((ip, 22), timeout=2)
            socket.close()
            ipaddress = ip
            break
        except:
            print('Waiting for node to come online.')
        sleep(2)
    if ipaddress is not None:
        break

banner = '''

UUID: {}
IPv6: {}
IPv4: {}
End of Life: {}

'''.format(node_uuid,
           node.ip6,
           node.ip4,
           node.end_of_life)

print(banner)

command = ('ssh root@{} -p 22 -oStrictHostKeyChecking=no'
           ' -oUserKnownHostsFile=/dev/null'.format(ipaddress))
os.system(command)

print(banner)

def fakemain():
    '''
    NOOP
    I need to fix this.
    '''
    a = 0
