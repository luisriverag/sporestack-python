#!/usr/bin/python3

"""
Cleaner interface into api_client, for the most part.
"""

import json
import sys
# FUTURE PYTHON 3.6: import secrets
import os
import logging
import time
from hashlib import sha256

import aaargh
import pyqrcode
from walkingliberty import WalkingLiberty

from . import api_client
from . import validate
from .version import __version__

cli = aaargh.App()

logging.basicConfig(level=logging.INFO)

CLEARNET_ENDPOINT = 'https://api.sporestack.com'
TOR_ENDPOINT = 'http://spore64'\
               'i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion'

API_ENDPOINT = CLEARNET_ENDPOINT

WAITING_PAYMENT_TO_PROCESS = 'Waiting for payment to process...'


def i_am_root():
    if os.getuid() == 0:
        return True
    else:
        return False


def random_machine_id():
    """
    Makes a random Machine ID.

    These can also be deterministic, but then it wouldn't be called "random".
    """
    # We could also use secrets.token_hex(32),
    # this may be more secure.
    # FUTURE PYTHON 3.6: random = secrets.token_bytes(64)
    random = os.urandom(64)
    machine_id = sha256(random).hexdigest()
    return machine_id


def make_payment(currency,
                 uri,
                 usd=None,
                 walkingliberty_wallet=None):
    if walkingliberty_wallet is not None:
        walkingliberty = WalkingLiberty(currency)
        txid = walkingliberty.pay(private_key=walkingliberty_wallet,
                                  uri=uri)
        logging.debug('WalkingLiberty txid: {}'.format(txid))
    else:
        premessage = '''Payment URI: {}
Pay *exactly* the specified amount. No more, no less. Pay within
one hour at the very most.
Resize your terminal and try again if QR code above is not readable.
Press ctrl+c to abort.'''
        message = premessage.format(uri)
        qr = pyqrcode.create(uri)
        print(qr.terminal(module_color='black',
                          background='white',
                          quiet_zone=1))
        print(message)
        if usd is not None:
            print('Approximate price in USD: {}'.format(usd))
        input('[Press enter once you have made payment.]')


# FIXME: ordering...
@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--host', type=str, default=None)
@cli.cmd_arg('--hostaccess', type=bool, default=False)
@cli.cmd_arg('--save', type=bool, default=True)
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--region', type=str, default=None)
@cli.cmd_arg('--managed', type=bool, default=False)
@cli.cmd_arg('--currency', type=str, default=None)
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--cores', type=int, default=1)
@cli.cmd_arg('--memory', type=int, default=1)
@cli.cmd_arg('--bandwidth', type=int, default=1)
@cli.cmd_arg('--ipv4', default='/32')
@cli.cmd_arg('--ipv6', default='/128')
@cli.cmd_arg('--disk', type=int, default=5)
@cli.cmd_arg('--days', type=int, required=True)
@cli.cmd_arg('--qemuopts', type=str, default=None)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=API_ENDPOINT)
@cli.cmd_arg('--want_topup', type=bool, default=False)
@cli.cmd_arg('--organization', type=str, default=None)
@cli.cmd_arg('--ipxescript', type=str, default=None)
@cli.cmd_arg('--ipxescript_stdin', type=bool, default=False)
@cli.cmd_arg('--ipxescript_file', type=str, default=None)
@cli.cmd_arg('--operating_system', type=str, default=None)
@cli.cmd_arg('--ssh_key', type=str, default=None)
@cli.cmd_arg('--ssh_key_file', type=str, default=None)
@cli.cmd_arg('--affiliate_amount', type=int, default=None)
@cli.cmd_arg('--affiliate_token', type=str, default=None)
def launch(vm_hostname,
           days,
           disk,
           memory,
           ipv4,
           ipv6,
           bandwidth,
           host=None,
           api_endpoint=API_ENDPOINT,
           cores=1,
           currency='bch',
           region=None,
           managed=False,
           organization=None,
           override_code=None,
           settlement_token=None,
           qemuopts=None,
           hostaccess=False,
           ipxescript=None,
           ipxescript_stdin=False,
           ipxescript_file=None,
           operating_system=None,
           ssh_key=None,
           ssh_key_file=None,
           walkingliberty_wallet=None,
           want_topup=False,
           save=True,
           affiliate_amount=None,
           affiliate_token=None):
    """
    Attempts to launch a server.
    """
    ipv4 = api_client.normalize_argument(ipv4)
    ipv6 = api_client.normalize_argument(ipv6)
    bandwidth = api_client.normalize_argument(bandwidth)
    want_topup = api_client.normalize_argument(want_topup)
    ipxescript_stdin = api_client.normalize_argument(ipxescript_stdin)

    if settlement_token is not None:
        if currency is None:
            currency = 'settlement'

    if machine_exists(vm_hostname):
        message = '{} already created.'.format(vm_hostname)
        raise ValueError(message)

    if host is None and api_endpoint is None:
        raise ValueError('host and/or api_endpoint must be set.')

    if ssh_key is not None and ssh_key_file is not None:
        raise ValueError('Only ssh_key or ssh_key_file can be set.')
    if ssh_key_file is not None:
        with open(ssh_key_file) as fp:
            ssh_key = fp.read()

    ipxe_not_none_or_false = 0
    for ipxe_option in [ipxescript, ipxescript_stdin, ipxescript_file]:
        if ipxe_option not in [False, None]:
            ipxe_not_none_or_false = ipxe_not_none_or_false + 1
    msg = 'Only set one of ipxescript, ipxescript_stdin, ipxescript_file'
    if ipxe_not_none_or_false > 1:
        raise ValueError(msg)
    if ipxescript_stdin is True:
        ipxescript = sys.stdin.read()
    elif ipxescript_file is not None:
        with open(ipxescript_file) as fp:
            ipxescript = fp.read()

    # FIXME: Hacky.
    if host == '127.0.0.1':
        if walkingliberty_wallet is None and settlement_token is None:
            if override_code is None:
                override_code = get_override_code()

    machine_id = random_machine_id()

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
                      cores=cores,
                      ipv4=ipv4,
                      ipv6=ipv6,
                      bandwidth=bandwidth,
                      currency=currency,
                      region=region,
                      organization=organization,
                      managed=managed,
                      override_code=override_code,
                      settlement_token=settlement_token,
                      qemuopts=qemuopts,
                      hostaccess=hostaccess,
                      api_endpoint=api_endpoint,
                      want_topup=want_topup,
                      affiliate_amount=affiliate_amount,
                      affiliate_token=affiliate_token,
                      retry=True)

    created_dict = create_vm(host)
    logging.debug(created_dict)
    if api_endpoint is not None:
        # Adjust host to whatever it gives us.
        host = created_dict['host']
    # This will be false at least the first time if paying with BTC or BCH.
    if created_dict['paid'] is False:
        uri = created_dict['payment']['uri']

        if 'usd' in created_dict['payment']:
            usd = created_dict['payment']['usd']
        else:
            usd = None

        make_payment(currency=currency,
                     uri=uri,
                     usd=usd,
                     walkingliberty_wallet=walkingliberty_wallet)

        tries = 360
        while tries > 0:
            tries = tries - 1
            logging.info(WAITING_PAYMENT_TO_PROCESS)
            # FIXME: Wait one hour in a smarter way.
            # Waiting for payment to set in.
            time.sleep(10)
            created_dict = create_vm(host)
            logging.debug(created_dict)
            if created_dict['paid'] is True:
                break

    if created_dict['created'] is False:
        tries = 360
        while tries > 0:
            logging.info('Waiting for server to build...')
            tries = tries + 1
            # Waiting for server to spin up.
            time.sleep(10)
            created_dict = create_vm(host)
            logging.debug(created_dict)
            if created_dict['created'] is True:
                break

    if created_dict['created'] is False:
        logging.warning(created_dict)
        # FIXME: Bad exception type.
        raise ValueError('Server creation failed, tries exceeded.')

    if 'host' not in created_dict:
        created_dict['host'] = host
    created_dict['vm_hostname'] = vm_hostname
    created_dict['machine_id'] = machine_id
    created_dict['api_endpoint'] = api_endpoint
    save_machine_info(created_dict)
    print(pretty_machine_info(created_dict), file=sys.stderr)
    return created_dict


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--currency', type=str, default=None)
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--days', type=int, required=True)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=None)
@cli.cmd_arg('--affiliate_amount', type=int, default=None)
@cli.cmd_arg('--affiliate_token', type=str, default=None)
def topup(vm_hostname,
          days,
          currency,
          override_code=None,
          settlement_token=None,
          walkingliberty_wallet=None,
          api_endpoint=None,
          affiliate_amount=None,
          affiliate_token=None):
    """
    tops up an existing vm.
    """
    if settlement_token is not None:
        if currency is None:
            currency = 'settlement'

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
                                currency=currency,
                                override_code=override_code,
                                api_endpoint=api_endpoint,
                                settlement_token=settlement_token,
                                affiliate_amount=affiliate_amount,
                                affiliate_token=affiliate_token,
                                retry=True)

    topped_dict = topup_vm()
    # This will be false at least the first time if paying with anything
    # but settlement.
    if topped_dict['paid'] is False:
        uri = topped_dict['payment']['uri']

        if 'usd' in topped_dict['payment']:
            usd = topped_dict['payment']['usd']
        else:
            usd = None

        make_payment(currency=currency,
                     uri=uri,
                     usd=usd,
                     walkingliberty_wallet=walkingliberty_wallet)

        tries = 360
        while tries > 0:
            logging.info(WAITING_PAYMENT_TO_PROCESS)
            tries = tries - 1
            # FIXME: Wait one hour in a smarter way.
            # Waiting for payment to set in.
            time.sleep(10)
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


def pretty_machine_info(info):
    msg = 'Hostname: {}\n'.format(info['vm_hostname'])
    msg += 'Machine ID (keep this secret!): {}\n'.format(info['machine_id'])
    if info['network_interfaces'][0] == {}:
        msg += 'SSH hostname: {}\n'.format(info['sshhostname'])
    else:
        if 'ipv6' in info['network_interfaces'][0]:
            msg += 'IPv6: {}\n'.format(info['network_interfaces'][0]['ipv6'])
        if 'ipv4' in info['network_interfaces'][0]:
            msg += 'IPv4: {}\n'.format(info['network_interfaces'][0]['ipv4'])
    expiration = info["expiration"]
    human_expiration = time.strftime('%Y-%m-%d %H:%M:%S %z',
                                     time.localtime(expiration))
    if 'running' in info:
        msg += 'Running: {}\n'.format(info['running'])
    msg += 'Expiration: {} ({})\n'.format(expiration, human_expiration)
    time_to_live = expiration - int(time.time())
    if time_to_live > 0:
        hours = time_to_live // 3600
        msg += 'Server will be deleted in {} hours.'.format(hours)
    else:
        hours = time_to_live * -1 // 3600
        msg += 'Server deleted {} hours ago.'.format(hours)
    return msg


@cli.cmd
def list():
    """
    List all locally known servers.
    """
    directory = machine_info_directory()
    infos = []
    for vm_hostname_json in os.listdir(directory):
        vm_hostname = vm_hostname_json.split('.')[0]
        saved_vm_info = get_machine_info(vm_hostname)
        upstream_vm_info = api_client.info(host=saved_vm_info['host'],
                                           machine_id=saved_vm_info['machine_id'],
                                           api_endpoint=saved_vm_info['api_endpoint'])
        saved_vm_info['expiration'] = upstream_vm_info['expiration']
        saved_vm_info['running'] = upstream_vm_info['running']
        infos.append(saved_vm_info)

    for info in infos:
        print()
        print(pretty_machine_info(info))

    print()
    return None


def remove(vm_hostname):
    """
    Removes a server's .json file.
    """
    os.remove(machine_info_directory() + "/" + vm_hostname + ".json")


@cli.cmd(name='remove')
@cli.cmd_arg('vm_hostname')
def remove_cli(vm_hostname):
    info = get_machine_info(vm_hostname)
    print(info)
    print(pretty_machine_info(info))
    remove(vm_hostname)
    print('{} removed.'.format(vm_hostname))


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
def info(vm_hostname, api_endpoint=None):
    """
    Info on the VM
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
    return api_client.info(host=host,
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
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
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
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
    return api_client.stop(host=host,
                           machine_id=machine_id,
                           api_endpoint=api_endpoint)


@cli.cmd
@cli.cmd_arg('vm_hostname')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def delete(vm_hostname, api_endpoint=None):
    """
    Deletes the VM (most likely prematurely.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    machine_id = machine_info['machine_id']
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
    api_client.delete(host=host,
                      machine_id=machine_id,
                      api_endpoint=api_endpoint)
    # Also remove the .json file
    remove(vm_hostname)


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
        # Not the safest for library use but this is generally just a CLI.
        # __name__ is not __main__ here, which is weird and tricky.
        ipxescript = sys.stdin.read()
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
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
    if api_endpoint is None:
        api_endpoint = machine_info['api_endpoint']
    return api_client.bootorder(host=host,
                                machine_id=machine_id,
                                bootorder=bootorder,
                                api_endpoint=api_endpoint)


def api_endpoint_to_host(api_endpoint):
    """
    Returns a likely workable host from just the endpoint.

    This would most likely come up if building from a host directly, without
    any API nodes.

    Input should look like http://foo.bar or https://foo.bar. We just return
    foo.bar.
    """
    return api_endpoint.split('/')[2]


@cli.cmd
@cli.cmd_arg('vm_hostname')
def serialconsole(vm_hostname):
    """
    ctrl + backslash to quit.
    """
    machine_info = get_machine_info(vm_hostname)
    host = machine_info['host']
    if host is None:
        host = api_endpoint_to_host(machine_info['api_endpoint'])
    machine_id = machine_info['machine_id']
    return api_client.serialconsole(host, machine_id)


@cli.cmd
@cli.cmd_arg('settlement_token')
@cli.cmd_arg('--dollars', type=int, default=None)
@cli.cmd_arg('--cents', type=int, default=None)
@cli.cmd_arg('--currency', type=str, default=None, required=True)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=API_ENDPOINT)
def settlement_token_enable(settlement_token,
                            dollars=None,
                            cents=None,
                            currency=None,
                            walkingliberty_wallet=None,
                            api_endpoint=None):
    """
    Enables a new settlement token.

    Cents is starting balance.
    """

    cents = _get_cents(dollars, cents)

    def enable_token():
        return api_client.settlement_token_enable(settlement_token=settlement_token,
                                                  cents=cents,
                                                  currency=currency,
                                                  api_endpoint=api_endpoint,
                                                  retry=True)

    enable_dict = enable_token()
    uri = enable_dict['payment_uri']
    usd = enable_dict['usd']

    make_payment(currency=currency,
                 uri=uri,
                 usd=usd,
                 walkingliberty_wallet=walkingliberty_wallet)

    tries = 360
    while tries > 0:
        logging.info(WAITING_PAYMENT_TO_PROCESS)
        tries = tries - 1
        # FIXME: Wait one hour in a smarter way.
        # Waiting for payment to set in.
        time.sleep(10)
        enable_dict = enable_token()
        if enable_dict['paid'] is True:
            break

    return True


def _get_cents(dollars, cents):
    validate._further_dollars_cents(dollars, cents)
    if dollars is not None:
        validate.cents(dollars)
        cents = dollars * 100
    return cents


@cli.cmd
@cli.cmd_arg('settlement_token')
@cli.cmd_arg('--dollars', type=int, default=None)
@cli.cmd_arg('--cents', type=int, default=None)
@cli.cmd_arg('--currency', type=str, default=None, required=True)
@cli.cmd_arg('--walkingliberty_wallet', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=API_ENDPOINT)
def settlement_token_add(settlement_token,
                         dollars=None,
                         cents=None,
                         currency=None,
                         walkingliberty_wallet=None,
                         api_endpoint=None):
    """
    Adds balance to an existing settlement token.
    """

    cents = _get_cents(dollars, cents)

    def add_to_token():
        return api_client.settlement_token_add(settlement_token,
                                               cents,
                                               currency=currency,
                                               api_endpoint=api_endpoint,
                                               retry=True)

    add_dict = add_to_token()
    uri = add_dict['payment_uri']
    usd = add_dict['usd']

    make_payment(currency=currency,
                 uri=uri,
                 usd=usd,
                 walkingliberty_wallet=walkingliberty_wallet)

    tries = 360
    while tries > 0:
        logging.info(WAITING_PAYMENT_TO_PROCESS)
        tries = tries - 1
        # FIXME: Wait one hour in a smarter way.
        # Waiting for payment to set in.
        time.sleep(10)
        add_dict = add_to_token()
        if add_dict['paid'] is True:
            break

    return True


@cli.cmd
@cli.cmd_arg('settlement_token')
@cli.cmd_arg('--api_endpoint', type=str, default=API_ENDPOINT)
def settlement_token_balance(settlement_token,
                             api_endpoint=None):
    """
    Gets balance for a settlement token.
    """

    return api_client.settlement_token_balance(settlement_token=settlement_token,
                                               api_endpoint=api_endpoint)


@cli.cmd
def settlement_token_generate():
    """
    Generates a settlement token that can be enabled.
    """
    return random_machine_id()


@cli.cmd
def version():
    """
    Returns the installed version.
    """
    return __version__


def main():
    output = cli.run()
    if output is True:
        exit(0)
    elif output is False:
        exit(1)
    elif output is None:
        exit(0)
    else:
        print(output)


if __name__ == '__main__':
    main()
