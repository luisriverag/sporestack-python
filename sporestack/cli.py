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
{}
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
        output = 'terminated for {} seconds'.format(dead_time)
    else:
        time_to_live = end_of_life - current_time
        output = '{} seconds till termination'.format(time_to_live)
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
            for item in node:
                if node[item] is not None:
                    print('{}: {}'.format(item, node[item]))
            print(ttl(node['end_of_life']))
            print('')
    if we_said_something is False:
        print('No active nodes, but you have expired nodes.')


def json_extractor_wrapper(args):
    """
    argparse wrapper for json_extractor
    """
    print(json_extractor(args.json_file, args.json_key))


def json_extractor(json_file, json_key):
    """
    Extracts a field from a json file.
    Helps with writing SporeStack files, especially
    extracting scripts.
    """
    with open(json_file) as json:
        data = yaml.safe_load(json)
        return data[json_key]


def sporestackfile_helper_wrapper(args):
    """
    argparse wrapper for sporestack_helper
    """
    print(sporestackfile_helper(days=args.days,
                                startupscript=args.startupscript,
                                cloudinit=args.cloudinit,
                                osid=args.osid,
                                name=args.name,
                                human_name=args.human_name,
                                description=args.description,
                                postlaunch=args.postlaunch,
                                mimetype=args.mimetype,
                                dcid=args.dcid,
                                flavor=args.flavor))


def sporestackfile_helper(days,
                          osid,
                          startupscript=None,
                          cloudinit=None,
                          name=None,
                          human_name=None,
                          description=None,
                          postlaunch=None,
                          mimetype=None,
                          dcid=None,
                          flavor=29):
    """
    Helps you write sporestack.json files.
    """
    if ' ' in name:
        stderr('Name cannot contain spaces.')
        raise
    # So much duplicity :-/.
    if postlaunch is not None:
        with open(postlaunch) as postlaunch_script:
            postlaunch = postlaunch_script.read()
    if cloudinit is not None:
        with open(cloudinit) as cloudinit_script:
            cloudinit = cloudinit_script.read()
    if startupscript is not None:
        with open(startupscript) as startupscript_script:
            startupscript = startupscript_script.read()
    if description is not None:
        with open(description) as description_file:
            description = description_file.read()
    data = {'days': days,
            'osid': osid,
            'name': name,
            'human_name': human_name,
            'description': description,
            'startupscript': startupscript,
            'cloudinit': cloudinit,
            'dcid': dcid,
            'flavor': flavor,
            'mimetype': mimetype,
            'postlaunch': postlaunch}
    return (json.dumps(data, sort_keys=True, indent=True))


def node_info_wrapper(args):
    """
    argparse wrapper for node_info()
    """
    print(node_info(uuid=args.uuid,
                    attribute=args.attribute))


def node_info(uuid, attribute=None):
    """
    attribute is a specific attribute that you want to return.
    """
    node_file = '{}.json'.format(uuid)
    node_file_path = os.path.join(DOT_FILE_PATH, node_file)
    with open(node_file_path) as node_file:
        node = yaml.safe_load(node_file)
    if attribute is None:
        return node
    else:
        return node[attribute]


def ssh_wrapper(args):
    """
    argparse wrapper for ssh()
    """
    output = ssh(uuid=args.uuid,
                 command=args.command,
                 stdin=args.stdin)
    if output is not None:
        # Python 3 and 2 support, respectively.
        try:
            print(output['stdout'].decode('utf-8'), end='')
            print(output['stderr'].decode('utf-8'), end='')
        except:
            print(output['stdout'], end='')
            print(output['stderr'], end='')
        exit(output['return_code'])


def ssh(uuid, command=None, stdin=None):
    """
    Connects to node via SSH. Meant for terminals.
    Probably want to split this into connectable and ssh?
    Much to do.
    Should support specifying a keyfile, maybe?
    Consider paramiko or Fabric?
    """
    node = node_info(uuid)
    hostname = node['hostname']
    while True:
        try:
            socket = create_connection((hostname, 22), timeout=2)
            socket.close()
            break
        except:
            stderr('Waiting for node to come online.')
        sleep(2)
    run_command = ['ssh', '-q', '-l', 'root', hostname,
                   '-oStrictHostKeyChecking=no',
                   '-oUserKnownHostsFile=/dev/null']
    if command is not None:
        run_command.append(command)
    else:
        if stdin is None:
            system_command = ''
            for word in run_command:
                system_command = '{} {}'.format(system_command, word)
            # Easier than allocating a PTY and all.
            os.system(system_command)
            return
    # For PTY-less operations.
    # If you're passing stdin, you probably aren't trying to | sporestack ssh..
    if stdin is not None:
        popen_stdin = PIPE
    else:
        # But if you don't set --stdin...
        popen_stdin = sys.stdin.fileno()
    process = Popen(run_command, stdin=popen_stdin, stderr=PIPE, stdout=PIPE)
    # Python 2 and 3 compatibility
    try:
        stdin = bytes(stdin, 'utf-8')
    except:
        stdin = stdin
    _stdout, _stderr = process.communicate(stdin)
    return_code = process.wait()
    return {'stdout': _stdout,
            'stderr': _stderr,
            'return_code': return_code}


def spawn_wrapper(args):
    """
    Wraps spawn(), invoked by argparse.
    Needs to be cleaned up.
    """
    spawn(uuid=args.uuid,
          days=args.days,
          sshkey=args.ssh_key,
          launch=args.launch,
          sporestackfile=args.sporestackfile,
          startupscript=args.startupscript,
          cloudinit=args.cloudinit,
          group=args.group,
          osid=args.osid,
          dcid=args.dcid,
          flavor=args.flavor,
          paycode=args.paycode,
          endpoint=args.endpoint)


def spawn(uuid,
          days=None,
          sshkey=None,
          launch=None,
          sporestackfile=None,
          group=None,
          osid=None,
          dcid=None,
          flavor=None,
          startupscript=None,
          postlaunch=None,
          connectafter=True,
          launch_profile=None,
          cloudinit=None,
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
    if startupscript is not None:
        connectafter = False
        with open(startupscript) as startupscript_file:
            startupscript = startupscript_file.read()
    # Yuck.
    if sporestackfile is not None or launch is not None:
        connectafter = False
        if sporestackfile is not None:
            with open(sporestackfile) as sporestack_json:
                settings = yaml.safe_load(sporestack_json)
                launch_profile = sporestackfile
        else:
            settings = sporestack.node_get_launch_profile(launch)
            launch_profile = settings['name']
        # Iffy on this. Let's let the user pick the days.
        # days = settings['days']
        osid = settings['osid']
        flavor = settings['flavor']
        startupscript = settings['startupscript']
        postlaunch = settings['postlaunch']
        cloudinit = settings['cloudinit']
    earlier_satoshis = None
    while True:
        try:
            node = sporestack.node(days=days,
                                   sshkey=sshkey,
                                   unique=uuid,
                                   osid=osid,
                                   dcid=dcid,
                                   flavor=flavor,
                                   startupscript=startupscript,
                                   cloudinit=cloudinit,
                                   paycode=paycode,
                                   endpoint=endpoint)
        except (ValueError, KeyboardInterrupt):
            raise
        except:
            sleep(2)
            stderr('Issue with SporeStack, retrying...')
            continue
        if node.payment_status is False:
            amount = "{0:.8f}".format(node.satoshis *
                                      0.00000001)
            uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
            premessage = '''UUID: {}
Bitcoin URI: {}
Pay with Bitcoin. Resize your terminal and try again if QR code is not visible.
Press ctrl+c to abort.'''
            message = premessage.format(uuid,
                                        uri)
            qr = pyqrcode.create(uri)
            if earlier_satoshis != node.satoshis:
                if earlier_satoshis is not None:
                    stderr('Payment changed, refreshing QR.')
                stderr(qr.terminal(module_color='black',
                                   background='white',
                                   quiet_zone=1))
                stderr(message)
                earlier_satoshis = node.satoshis
        else:
            stderr('Node being built...')
        if node.creation_status is True:
            break
        sleep(2)

    banner = BANNER.format(node.hostname,
                           node.end_of_life,
                           ttl(node.end_of_life))
    if not os.path.isdir(DOT_FILE_PATH):
        os.mkdir(DOT_FILE_PATH, 0o700)
    node_file_path = '{}/{}.json'.format(DOT_FILE_PATH, uuid)
    node_dump = {'ip4': node.ip4,
                 'ip6': node.ip6,
                 'hostname': node.hostname,
                 'end_of_life': node.end_of_life,
                 'uuid': uuid,
                 'launch_profile': launch_profile,
                 'group': group}
    with open(node_file_path, 'w') as node_file:
        json.dump(node_dump, node_file)
    if postlaunch is not None:
        print(ssh(uuid, stdin=postlaunch)['stdout'], end='')
        return
    if connectafter is True:
        stderr(banner)
        ssh(uuid)
        stderr(banner)
        return
    else:
        # Yuck
        print(uuid)
        return


def nodemeup():
    """
    Ugly deprecation notice.
    """
    print('nodemeup is deprecated. Please use "sporestack spawn", instead.')
    exit(1)


def main():
    options = sporestack.node_options()
    launch_profiles = sporestack.node_get_launch_profile('index')

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawTextHelpFormatter):
        """
        This makes help honor newlines and shows defaults.
        https://bugs.python.org/issue21633
        http://stackoverflow.com/questions/18462610/
        """
        pass
    parser = argparse.ArgumentParser(description='SporeStack.com CLI.')
    launch_help = ''
    for profile in launch_profiles:
        launch_help += '{}: {}: {}\n'.format(profile['name'],
                                             profile['human_name'],
                                             profile['description'])
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
    ssh_subparser.add_argument('--command',
                               help='Command to run over SSH',
                               default=None)

    node_info_sp = subparser.add_parser('node_info',
                                        help='Return info about a node.')
    node_info_sp.set_defaults(func=node_info_wrapper)
    node_info_sp.add_argument('uuid', help='UUID of node to connect to.')
    node_info_sp.add_argument('--attribute',
                              help='Which attribute you want to return.',
                              default=None)

    json_extractor_help = 'Helps you extract fields from json files.'
    json_extractor_subparser = subparser.add_parser('json_extractor',
                                                    help=json_extractor_help)
    json_extractor_subparser.set_defaults(func=json_extractor_wrapper)
    json_extractor_subparser.add_argument('json_file',
                                          help='json file.')
    json_extractor_subparser.add_argument('json_key',
                                          help='json key.')

    ssfh_help = 'Helps you write sporestack.json files.'
    ssfh_subparser = subparser.add_parser('sporestackfile_helper',
                                          help=ssfh_help)
    ssfh_subparser.set_defaults(func=sporestackfile_helper_wrapper)
    ssfh_subparser.add_argument('--cloudinit',
                                help='cloudinit data.')
    ssfh_subparser.add_argument('--startupscript',
                                help='startup script file.')
    ssfh_subparser.add_argument('--postlaunch',
                                help='postlaunch script file.',
                                default=None)
    ssfh_subparser.add_argument('--days',
                                help='Days',
                                default=1,
                                type=int)
    ssfh_subparser.add_argument('--name',
                                help='Name',
                                required=True)
    ssfh_subparser.add_argument('--human_name',
                                help='Human readable name',
                                required=True)
    ssfh_subparser.add_argument('--description',
                                help='Description Markdown text file')
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
                                help='Flavor',
                                type=int,
                                default=29)
    ssfh_subparser.add_argument('--mimetype',
                                help='Suggested MIME type of stdout',
                                default='text/plain')

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
    spawn_subparser.add_argument('--launch',
                                 help=launch_help,
                                 default=None)
    spawn_subparser.add_argument('--sporestackfile',
                                 help='SporeStack JSON file.',
                                 default=None)
    spawn_subparser.add_argument('--startupscript',
                                 help='startup script file.',
                                 default=None)
    spawn_subparser.add_argument('--cloudinit',
                                 help='cloudinit file.',
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
