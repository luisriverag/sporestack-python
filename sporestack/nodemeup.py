"""
Build a server and SSH into it. Server will last for a day.
"""

import argparse
from uuid import uuid4 as random_uuid
from time import sleep
import os
from socket import create_connection

import pyqrcode
import sporestack

options = sporestack.node_options()

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

osid_help = 'Default: 230 (FreeBSD 11)\n'
for osid in options['osid']:
    name = options['osid'][osid]['name']
    osid_help += '{}: {}\n'.format(osid, name)

dcid_help = 'Default: (probably) 3 (Dallas)\n'
for dcid in options['dcid']:
    name = options['dcid'][dcid]['name']
    dcid_help += '{}: {}\n'.format(dcid, name)

flavor_help = 'Default: 29 (768MiB)\n'
for flavor in options['flavor']:
    help_line = '{}: RAM: {}, VCPUs: {}, DISK: {}\n'
    ram = options['flavor'][flavor]['ram']
    disk = options['flavor'][flavor]['disk']
    vcpus = options['flavor'][flavor]['vcpu_count']
    flavor_help += help_line.format(flavor, ram, vcpus, disk)

parser.add_argument('--osid', help=osid_help, type=int)
parser.add_argument('--dcid', help=dcid_help, type=int)
parser.add_argument('--flavor', help=flavor_help, type=int)
parser.add_argument('--days', help='Days to live: 1-28. Defaults to 1.',
                    type=int, default=1)
parser.add_argument('--uuid', help='Force a specific UUID.',
                    default=str(random_uuid()))
parser.add_argument('--endpoint', help=argparse.SUPPRESS, default=None)
parser.add_argument('--paycode', help=argparse.SUPPRESS, default=None)

args = parser.parse_args()

ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

try:
    with open(ssh_key_path) as ssh_key_file:
        sshkey = ssh_key_file.read()
except:
    print('You need to have an SSH key file. Run ssh-keygen.')
    exit(1)

while True:
    node = sporestack.node(days=args.days,
                           sshkey=sshkey,
                           unique=args.uuid,
                           osid=args.osid,
                           dcid=args.dcid,
                           flavor=args.flavor,
                           paycode=args.paycode,
                           endpoint=args.endpoint)
    if node.payment_status is False:
        amount = "{0:.8f}".format(node.satoshis *
                                  0.00000001)
        uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
        premessage = '''UUID: {}
{}
Pay with Bitcoin. Resize your terminal if QR code is not visible.'''
        message = premessage.format(args.uuid,
                                    uri)
        qr = pyqrcode.create(uri)
        # Show in reverse and normal modes so that it works on any terminal.
        print(qr.terminal(module_color='black',
                          background='white'))
        print(message)
        sleep(2)
        print(qr.terminal(module_color='white',
                          background='black'))
        print(message)
    else:
        print('Node being built...')
    if node.creation_status is True:
        break
    sleep(2)

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

'''.format(args.uuid,
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
    return True
