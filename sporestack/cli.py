"""
sporestack CLI client
"""

import argparse
from uuid import uuid4 as random_uuid
from time import sleep, time
import os
from socket import create_connection
import json

import pyqrcode
import sporestack
import yaml

DOT_FILE_PATH = '{}/.sporestack'.format(os.getenv('HOME'))

default_ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

BANNER = '''
UUID: {}
IPv6: {}
IPv4: {}
End of Life: {} ({})
'''


def ttl(end_of_life):
    """
    Human readable time remaining.
    Needs work. This is weird.
    """
    current_time = int(time())
    if current_time > end_of_life:
        dead_time = current_time - end_of_life
        output = 'dead for {} seconds'.format(dead_time)
    else:
        time_to_live = end_of_life - current_time
        output = '{} seconds'.format(time_to_live)
    return output


def list(_):
    """
    List SporeStack instances that you've launched.
    This is ugly. Needs to be cleaned up and made less fragile.
    """
    if not os.path.isdir(DOT_FILE_PATH):
        print('Run spawn, first.')
        exit(1)
    for node_file in os.listdir(DOT_FILE_PATH):
        node = node_info(node_file.split('.')[0])
        banner = BANNER.format(node['uuid'],
                               node['ip6'],
                               node['ip4'],
                               node['end_of_life'],
                               ttl(node['end_of_life']))
        print(banner)


def node_info(uuid):
    node_file = '{}.json'.format(uuid)
    node_file_path = os.path.join(DOT_FILE_PATH, node_file)
    with open(node_file_path) as node_file:
        node = yaml.safe_load(node_file)
        return node


def ssh(uuid):
    """
    Connects to node via SSH. Meant for terminals.
    Probably want to split this into connectable and ssh?
    Much to do.
    Should support specifying a keyfile, maybe?
    """
    # There must be a better way to do this. So ugly!
    # hug? Another argument parser? Something?
    if not isinstance(uuid, basestring):
        node_uuid = uuid.uuid
    else:
        node_uuid = uuid
    node = node_info(node_uuid)
    ipaddress = None
    while True:
        for ip in [node['ip6'], node['ip4']]:
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
    command = ('ssh root@{} -p 22 -oStrictHostKeyChecking=no'
               ' -oUserKnownHostsFile=/dev/null'.format(ipaddress))
    os.system(command)


def spawn(args):
    try:
        with open(args.ssh_key) as ssh_key_file:
            # Try to strip off any SSH key comments.
            # Maybe this should be in __init__.py?
            unclean_ssh_key = ssh_key_file.read()
            sshkey_prefix = unclean_ssh_key.split(' ')[0]
            sshkey_key = unclean_ssh_key.split(' ')[1]
            commentless_key = sshkey_prefix + ' ' + sshkey_key
            sshkey = commentless_key
    except:
        pre_message = 'Unable to open {}. Did you run ssh-keygen?'
        message = pre_message.format(args.ssh_key)
        print(message)
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
            # Show in reverse and normal modes so that it works on any
            # terminal.
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

    banner = BANNER.format(args.uuid,
                           node.ip6,
                           node.ip4,
                           node.end_of_life,
                           ttl(node.end_of_life))
    if not os.path.isdir(DOT_FILE_PATH):
        os.mkdir(DOT_FILE_PATH, 0700)
    node_file_path = '{}/{}.json'.format(DOT_FILE_PATH, args.uuid)
    node_dump = {'ip4': node.ip4,
                 'ip6': node.ip6,
                 'end_of_life': node.end_of_life,
                 'uuid': args.uuid}
    with open(node_file_path, 'w') as node_file:
        json.dump(node_dump, node_file)
    print(banner)
    ssh(args.uuid)
    print(banner)


def nodemeup():
    """
    Ugly deprecation notice.
    """
    print('nodemeup is deprecated. Please use "sporestack", instead.')
    exit(1)


def main():
    options = sporestack.node_options()

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
        """
        This makes help honor newlines and shows defaults.
        https://bugs.python.org/issue21633
        http://stackoverflow.com/questions/18462610/
        """
        pass
    parser = argparse.ArgumentParser(description='SporeStack.com CLI.')
    osid_help = ''
    for osid in sorted(options['osid'], key=int):
        name = options['osid'][osid]['name']
        osid_help += '{}: {}\n'.format(osid, name)
    dcid_help = ''
    for dcid in sorted(options['dcid'], key=int):
        name = options['dcid'][dcid]['name']
        dcid_help += '{}: {}\n'.format(dcid, name)
    flavor_help = ''
    for flavor in sorted(options['flavor'], key=int):
        help_line = '{}: RAM: {}, VCPUs: {}, DISK: {}\n'
        ram = options['flavor'][flavor]['ram']
        disk = options['flavor'][flavor]['disk']
        vcpus = options['flavor'][flavor]['vcpu_count']
        flavor_help += help_line.format(flavor, ram, vcpus, disk)
    subparser = parser.add_subparsers()
    spawn_subparser = subparser.add_parser('spawn',
                                           help='Spawns a node.',
                                           formatter_class=CustomFormatter)
    spawn_subparser.set_defaults(func=spawn)
    list_subparser = subparser.add_parser('list', help='Lists nodes.')
    list_subparser.set_defaults(func=list)
    ssh_subparser = subparser.add_parser('ssh',
                                         help='Connect to node.')
    ssh_subparser.set_defaults(func=ssh)
    ssh_subparser.add_argument('uuid', help='UUID of node to connect to.')
    spawn_subparser.add_argument('--osid',
                                 help=osid_help,
                                 type=int,
                                 default=230)
    spawn_subparser.add_argument('--dcid', help=dcid_help, type=int, default=3)
    spawn_subparser.add_argument('--flavor',
                                 help=flavor_help,
                                 type=int,
                                 default=29)
    spawn_subparser.add_argument('--days',
                                 help='Days to live: 1-28.',
                                 type=int, default=1)
    spawn_subparser.add_argument('--uuid',
                                 help=argparse.SUPPRESS,
                                 default=str(random_uuid()))
    spawn_subparser.add_argument('--endpoint',
                                 help=argparse.SUPPRESS,
                                 default=None)
    spawn_subparser.add_argument('--paycode',
                                 help=argparse.SUPPRESS,
                                 default=None)
    default_ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))
    spawn_subparser.add_argument('--ssh_key',
                                 help='SSH public key.',
                                 default=default_ssh_key_path)
    args = parser.parse_args()
    # This calls whatever the given command is. (spawn, list, etc)
    args.func(args)

if __name__ == '__main__':
    main()
