"""
sporestack CLI client
"""

from __future__ import print_function
import argparse
from uuid import uuid4 as random_uuid
from time import sleep, time
import os
from socket import create_connection
import json
import sys
from subprocess import Popen, PIPE

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


def stderr(*args, **kwargs):
    """
    http://stackoverflow.com/a/14981125
    """
    print(*args, file=sys.stderr, **kwargs)


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
    current_time = int(time())
    we_said_something = False
    for node_file in os.listdir(DOT_FILE_PATH):
        node = node_info(node_file.split('.')[0])
        if current_time < node['end_of_life']:
            we_said_something = True
            banner = BANNER.format(node['uuid'],
                                   node['ip6'],
                                   node['ip4'],
                                   node['end_of_life'],
                                   ttl(node['end_of_life']))
            print(banner)
            if node['group'] is not None:
                print('Group: {}'.format(node['group']))
    if we_said_something is False:
        print('No active nodes, but you have expired nodes.')


def sporestackfile_helper_wrapper(args):
    """
    argparse wrapper for sporestack_helper
    """
    print(sporestackfile_helper(days=args.days,
                                startupscript=args.startupscript,
                                osid=args.osid,
                                postlaunch=args.postlaunch,
                                dcid=args.dcid,
                                flavor=args.flavor))


def sporestackfile_helper(days,
                          startupscript,
                          osid,
                          postlaunch=None,
                          dcid=None,
                          flavor=29):
    """
    Helps you write sporestack.json files.
    """
    if postlaunch is not None:
        with open(postlaunch) as postlaunch_script:
            postlaunch = postlaunch_script.read()
    with open(startupscript) as script:
            data = {'days': days,
                    'osid': osid,
                    'startupscript': script.read(),
                    'dcid': dcid,
                    'flavor': flavor,
                    'postlaunch': postlaunch}
    return (json.dumps(data, sort_keys=True, indent=True))


def node_info(uuid):
    node_file = '{}.json'.format(uuid)
    node_file_path = os.path.join(DOT_FILE_PATH, node_file)
    with open(node_file_path) as node_file:
        node = yaml.safe_load(node_file)
        return node


def ssh_wrapper(args):
    """
    argparse wrapper for ssh()
    """
    possible_output = ssh(uuid=args.uuid,
                          stdin=args.stdin)
    if possible_output is not None:
        print(possible_output, end='')


def ssh(uuid, stdin=None):
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
                stderr('Waiting for node to come online.')
            sleep(2)
        if ipaddress is not None:
            break
    command = ('ssh root@{} -p 22 -oStrictHostKeyChecking=no'
               ' -oUserKnownHostsFile=/dev/null'.format(ipaddress))
    if stdin is None:
        os.system(command)
    else:
        command = ['ssh', '-l', 'root', ipaddress,
                   '-oStrictHostKeyChecking=no',
                   '-oUserKnownHostsFile=/dev/null']
        process = Popen(command, stdin=PIPE, stderr=PIPE, stdout=PIPE)
        _stdout, _stderr = process.communicate(stdin)
        return_code = process.wait()
        if return_code != 0:
            stderr(_stderr)
            raise
        return _stdout


def spawn_wrapper(args):
    """
    Wraps spawn(), invoked by argparse.
    Needs to be cleaned up.
    """
    spawn(days=args.days,
          uuid=args.uuid,
          sshkey=args.ssh_key,
          sporestackfile=args.sporestackfile,
          group=args.group,
          osid=args.osid,
          dcid=args.dcid,
          flavor=args.flavor,
          paycode=args.paycode,
          endpoint=args.endpoint)


def spawn(days,
          uuid,
          sshkey=None,
          sporestackfile=None,
          group=None,
          osid=None,
          dcid=None,
          flavor=None,
          startupscript=None,
          postlaunch=None,
          connectafter=True,
          paycode=None,
          endpoint=None):
    if sshkey is not None:
        try:
            with open(sshkey) as ssh_key_file:
                sshkey = ssh_key_file.read()
        except:
            pre_message = 'Unable to open {}. Did you run ssh-keygen?'
            message = pre_message.format(sshkey)
            stderr(message)
            exit(1)
    if sporestackfile is not None:
        connectafter = False
        with open(sporestackfile) as sporestack_json:
            settings = yaml.safe_load(sporestack_json)
            osid = settings['osid']
            startupscript = settings['startupscript']
            postlaunch = settings['postlaunch']
            for setting in ['dcid',
                            'flavor']:
                if eval(setting) is None:
                    if setting in settings:
                        exec(setting + ' = ' + str(settings[setting]))
    while True:
        node = sporestack.node(days=days,
                               sshkey=sshkey,
                               unique=uuid,
                               osid=osid,
                               dcid=dcid,
                               flavor=flavor,
                               startupscript=startupscript,
                               paycode=paycode,
                               endpoint=endpoint)
        if node.payment_status is False:
            amount = "{0:.8f}".format(node.satoshis *
                                      0.00000001)
            uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
            premessage = '''UUID: {}
{}
Pay with Bitcoin. Resize your terminal if QR code is not visible.'''
            message = premessage.format(uuid,
                                        uri)
            qr = pyqrcode.create(uri)
            # Show in reverse and normal modes so that it works on any
            # terminal.
            stderr(qr.terminal(module_color='black',
                               background='white'))
            stderr(message)
            sleep(2)
            stderr(qr.terminal(module_color='white',
                               background='black'))
            stderr(message)
        else:
            stderr('Node being built...')
        if node.creation_status is True:
            break
        sleep(2)

    banner = BANNER.format(uuid,
                           node.ip6,
                           node.ip4,
                           node.end_of_life,
                           ttl(node.end_of_life))
    if not os.path.isdir(DOT_FILE_PATH):
        os.mkdir(DOT_FILE_PATH, 0700)
    node_file_path = '{}/{}.json'.format(DOT_FILE_PATH, uuid)
    node_dump = {'ip4': node.ip4,
                 'ip6': node.ip6,
                 'end_of_life': node.end_of_life,
                 'uuid': uuid,
                 'group': group}
    with open(node_file_path, 'w') as node_file:
        json.dump(node_dump, node_file)
    if postlaunch is not None:
        print(ssh(uuid, stdin=postlaunch), end='')
    if connectafter is True:
        stderr(banner)
        ssh(uuid)
        stderr(banner)


def nodemeup():
    """
    Ugly deprecation notice.
    """
    print('nodemeup is deprecated. Please use "sporestack spawn", instead.')
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
    spawn_subparser.set_defaults(func=spawn_wrapper)
    list_subparser = subparser.add_parser('list', help='Lists nodes.')
    list_subparser.set_defaults(func=list)
    ssh_subparser = subparser.add_parser('ssh',
                                         help='Connect to node.')
    ssh_subparser.set_defaults(func=ssh_wrapper)
    ssh_subparser.add_argument('uuid', help='UUID of node to connect to.')
    ssh_subparser.add_argument('--stdin',
                               help='Send to stdin and return stdout',
                               default=None)

    ssfh_help = 'Helps you write sporestack.json files.'
    ssfh_subparser = subparser.add_parser('sporestackfile_helper',
                                          help=ssfh_help)
    ssfh_subparser.set_defaults(func=sporestackfile_helper_wrapper)
    ssfh_subparser.add_argument('startupscript',
                                help='startup script file.')
    ssfh_subparser.add_argument('--postlaunch',
                                help='postlaunch script file.',
                                default=None)
    ssfh_subparser.add_argument('--days',
                                help='Days',
                                required=True,
                                type=int)
    ssfh_subparser.add_argument('--osid',
                                help='OSID',
                                required=True,
                                type=int,
                                default=None)
    ssfh_subparser.add_argument('--dcid',
                                help='DCID',
                                type=int,
                                default=None)
    ssfh_subparser.add_argument('--flavor',
                                help='DCID',
                                type=int,
                                default=29)

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
    spawn_subparser.add_argument('--sporestackfile',
                                 help='SporeStack JSON file.',
                                 default=None)
    spawn_subparser.add_argument('--group',
                                 help='Arbitrary group to associate node with',
                                 default=None)
    args = parser.parse_args()
    # This calls the function or wrapper function, depending on what we set
    # above.
    args.func(args)

if __name__ == '__main__':
    main()
