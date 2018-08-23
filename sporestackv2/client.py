#!/usr/bin/python3

"""
Cleaner interface into api_client, for the most part.
"""

import json
import sys
# FUTURE PYTHON 3.6: import secrets
import os
import logging
from hashlib import sha256
from time import sleep

import aaargh
from walkingliberty import WalkingLiberty

from . import api_client

cli = aaargh.App()

logging.basicConfig(level=logging.INFO)

API_ENDPOINT = 'https://api.sporestack.com'


def i_am_root():
    if os.getuid() == 0:
        return True
    else:
        return False


def make_random_machine_id():
    """
    For now, make a random machine_id.
    This can be completely deterministic
    if we please. But, this is easier for now.
    """
    # We could also use secrets.token_hex(32),
    # this may be more secure.
    # FUTURE PYTHON 3.6: random = secrets.token_bytes(64)
    random = os.urandom(64)
    machine_id = sha256(random).hexdigest()
    return machine_id


# FIXME: ordering...
@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--host', type=str, default=None)
@cli.cmd_arg('--hostaccess', type=bool, default=False)
@cli.cmd_arg('--save', type=bool, default=True)
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--managed', type=bool, default=False)
@cli.cmd_arg('--currency', type=str, default=None)
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--cores', type=int, default=1)
@cli.cmd_arg('--memory', type=int, required=True)
@cli.cmd_arg('--bandwidth', type=int, required=True)
@cli.cmd_arg('--ipv4', required=True)
@cli.cmd_arg('--ipv6', required=True)
@cli.cmd_arg('--disk', type=int, required=True)
@cli.cmd_arg('--days', type=int, default=0)
@cli.cmd_arg('--refund_address', type=str, default=None)
@cli.cmd_arg('--qemuopts', type=str, default=None)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=API_ENDPOINT)
@cli.cmd_arg('--want_topup', type=bool, default=False)
@cli.cmd_arg('--organization', type=str, default=None)
@cli.cmd_arg('--ipxescript', type=str, default=None)
@cli.cmd_arg('--ipxescript_stdin', type=bool, default=False)
@cli.cmd_arg('--operating_system', type=str, default=None)
@cli.cmd_arg('--ssh_key', type=str, default=None)
def launch(vm_hostname,
           days,
           disk,
           memory,
           ipv4,
           ipv6,
           bandwidth,
           host=None,
           api_endpoint=API_ENDPOINT,
           refund_address=None,
           cores=1,
           currency='bch',
           managed=False,
           organization=None,
           override_code=None,
           settlement_token=None,
           qemuopts=None,
           hostaccess=False,
           ipxescript=None,
           ipxescript_stdin=False,
           operating_system=None,
           ssh_key=None,
           walkingliberty_wallet=None,
           want_topup=False,
           save=True):
    """
    Pass ipxe script via stdin.

    FIXME: want_topup only works when using api_endpoint.
    """
    ipv4 = api_client.normalize_argument(ipv4)
    ipv6 = api_client.normalize_argument(ipv6)
    bandwidth = api_client.normalize_argument(bandwidth)
    want_topup = api_client.normalize_argument(want_topup)
    ipxescript_stdin = api_client.normalize_argument(ipxescript_stdin)

    if host is None and api_endpoint is None:
        raise ValueError('host and/or api_endpoint must be set.')

    if machine_exists(vm_hostname):
        message = '{} already created.'.format(vm_hostname)
        raise ValueError(message)
    # FIXME: Hacky.
    if host == '127.0.0.1':
        if walkingliberty_wallet is None and settlement_token is None:
            if override_code is None:
                override_code = get_override_code()

    msg = 'ipxescript must be None with ipxescript_stdin set to True'
    if ipxescript is not None:
        if ipxescript_stdin is True:
            raise ValueError(msg)

    if ipxescript_stdin is True:
        ipxescript = sys.stdin.read()

    machine_id = make_random_machine_id()

    def create_vm(host):
        create = api_client.launch
        return create(host=host,
                      machine_id=machine_id,
                      days=days,
                      disk=disk,
                      memory=memory,
                      ipxescript=ipxescript,
                      operating_system=operating_system,
                      ssh_key=ssh_key,
                      refund_address=refund_address,
                      cores=cores,
                      ipv4=ipv4,
                      ipv6=ipv6,
                      bandwidth=bandwidth,
                      currency=currency,
                      organization=organization,
                      managed=managed,
                      override_code=override_code,
                      settlement_token=settlement_token,
                      qemuopts=qemuopts,
                      hostaccess=hostaccess,
                      api_endpoint=api_endpoint,
                      want_topup=want_topup,
                      retry=True)

    created_dict = create_vm(host)
    if api_endpoint is not None:
        # Adjust host to whatever it gives us.
        host = created_dict['host']
    if created_dict['paid'] is False:
        if walkingliberty_wallet is None:
            return created_dict
        else:
            walkingliberty = WalkingLiberty(currency)
            address = created_dict['payment']['address']
            satoshis = created_dict['payment']['amount']
            txid = walkingliberty.send(private_key=walkingliberty_wallet,
                                       address=address,
                                       satoshis=satoshis)
            logging.debug('txid: {}'.format(txid))
            # Off by one? Meh.
            tries = 0
            while tries != 10:
                logging.info('Waiting for payment to process...')
                tries = tries + 1
                # Waiting for payment to set in.
                sleep(10)
                created_dict = create_vm(host)
                if created_dict['paid'] is True:
                    break

    if created_dict['created'] is False:
        tries = 0
        while tries != 10:
            logging.info('Waiting for server to build...')
            tries = tries + 1
            # Waiting for payment to set in.
            sleep(10)
            created_dict = create_vm(host)
            if created_dict['created'] is True:
                break

    if 'host' not in created_dict:
        created_dict['host'] = host
    created_dict['vm_hostname'] = vm_hostname
    created_dict['machine_id'] = machine_id
    created_dict['api_endpoint'] = api_endpoint
    save_machine_info(created_dict)
    return created_dict


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--currency', type=str, default=None, required=True)
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--days', type=int, required=True)
@cli.cmd_arg('--refund_address', type=str, default=None)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def topup(vm_hostname,
          days,
          currency,
          refund_address=None,
          override_code=None,
          settlement_token=None,
          walkingliberty_wallet=None,
          api_endpoint=None):
    """
    tops up an existing vm.
    """

    if not machine_exists(vm_hostname):
        message = '{} does not exist.'.format(vm_hostname)
        raise ValueError(message)
    machine_info = get_machine_info(vm_hostname)
    machine_id = machine_info['machine_id']
    # hostname of the host
    host = machine_info['host']
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']

    if api_endpoint is None:
        # FIXME: Hacky.
        if host == '127.0.0.1':
            if walkingliberty_wallet is None and settlement_token is None:
                if override_code is None:
                    override_code = get_override_code()

    def topup_vm():
        return api_client.topup(host=host,
                                machine_id=machine_id,
                                days=days,
                                refund_address=refund_address,
                                currency=currency,
                                override_code=override_code,
                                api_endpoint=api_endpoint,
                                settlement_token=settlement_token,
                                retry=True)

    topped_dict = topup_vm()
    if topped_dict['paid'] is False:
        if walkingliberty_wallet is None:
            return topped_dict
        else:
            walkingliberty = WalkingLiberty(currency)
            address = topped_dict['payment']['address']
            satoshis = topped_dict['payment']['amount']
            txid = walkingliberty.send(private_key=walkingliberty_wallet,
                                       address=address,
                                       satoshis=satoshis)
            logging.debug('txid: {}'.format(txid))
            tries = 0
            while tries != 10:
                logging.info('Waiting for payment to process...')
                tries = tries + 1
                # Waiting for payment to set in.
                sleep(10)
                topped_dict = topup_vm()
                if topped_dict['paid'] is True:
                    break

    machine_info['expiration'] = topped_dict['expiration']
    save_machine_info(machine_info, overwrite=True)
    return machine_info['expiration']


def machine_info_directory():
    if i_am_root():
        directory = '/etc/sporestackv2'
    else:
        directory = os.path.join(os.getenv('HOME'), '.sporestackv2')
    return directory


def save_machine_info(machine_info, overwrite=False):
    """
    Save info to disk.
    """
    if overwrite is True:
        mode = 'w'
    else:
        mode = 'x'
    os.umask(0o0077)
    directory = machine_info_directory()
    if not os.path.exists(directory):
        os.mkdir(directory)
    vm_hostname = machine_info['vm_hostname']
    json_path = os.path.join(directory, '{}.json'.format(vm_hostname))
    with open(json_path, mode) as json_file:
        json.dump(machine_info, json_file)
    return True


def get_machine_info(vm_hostname):
    """
    Get info from disk.
    """
    directory = machine_info_directory()
    if not machine_exists(vm_hostname):
        msg = '{} does not exist in {}'.format(vm_hostname, directory)
        raise ValueError(msg)
    json_path = os.path.join(directory, '{}.json'.format(vm_hostname))
    with open(json_path) as json_file:
        machine_info = json.load(json_file)
    if machine_info['vm_hostname'] != vm_hostname:
        raise ValueError('vm_hostname does not match filename.')
    return machine_info


def machine_exists(vm_hostname):
    """
    Check if the VM exists locally in /etc/sporestackv2 or ~/.sporestackv2
    """
    directory = machine_info_directory()
    file_path = os.path.join(directory, '{}.json'.format(vm_hostname))
    if os.path.exists(file_path):
        return True
    else:
        return False


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('attribute')
def get_attribute(vm_hostname, attribute):
    """
    Returns an attribute about the VM.
    """
    machine_info = get_machine_info(vm_hostname)
    return machine_info[attribute]


def get_override_code():
    """
    Attempts to procure the override code for
    localhost spawns.
    """
    try:
        with open('/etc/vmmanagement.override_code') as fp:
            override_code = fp.read().strip('\n')
    except Exception:
        override_code = None
    return override_code


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def exists(vm_hostname, api_endpoint=None):
    """
    Checks if the VM still exists.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
    return api_client.exists(host=host,
                             machine_id=machine_id,
                             api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def info(vm_hostname, api_endpoint=None):
    """
    Info on the VM
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.info(host=host,
                           machine_id=machine_id,
                           api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def status(vm_hostname, api_endpoint=None):
    """
    Checks if the VM is started or stopped.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.status(host=host,
                             machine_id=machine_id,
                             api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def start(vm_hostname, api_endpoint=None):
    """
    Boots the VM.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.start(host=host,
                            machine_id=machine_id,
                            api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def stop(vm_hostname, api_endpoint=None):
    """
    Immediately kills the VM.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.stop(host=host,
                           machine_id=machine_id,
                           api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def ipxescript(vm_hostname, ipxescript=None, api_endpoint=None):
    """
    Trying to make this both useful as a CLI tool and
    as a library. Not really sure how to do that best.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    if ipxescript is None:
        if __name__ == '__main__':
            ipxescript = sys.stdin.read()
        else:
            raise ValueError('ipxescript must be set.')
    return api_client.ipxescript(host=host,
                                 machine_id=machine_id,
                                 ipxescript=ipxescript,
                                 api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('bootorder')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def bootorder(vm_hostname, bootorder, api_endpoint=None):
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.bootorder(host=host,
                                machine_id=machine_id,
                                bootorder=bootorder,
                                api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
def serialconsole(vm_hostname):
    """
    ctrl + \ to quit.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    return api_client.serialconsole(host, machine_id)


def main():
    output = cli.run()
    if output is True:
        exit(0)
    elif output is False:
        exit(1)
    else:
        print(output)


if __name__ == '__main__':
    main()
