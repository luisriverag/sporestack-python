#!/usr/bin/python3

import logging
import sys
from time import sleep

import aaargh
import requests

from . import ssh
from . import validate

cli = aaargh.App()

LATEST_API_VERSION = 2


def api_request(url, json_params=None, get_params=None, retry=False):
    try:
        if json_params is None:
            request = requests.get(url, params=get_params, timeout=330)
        else:
            request = requests.post(url, json=json_params, timeout=330)
    except Exception as e:
        if retry is True:
            logging.warning('Got an error, but retrying: {}'.format(e))
            sleep(5)
            # Try again.
            return api_request(url, json_params, retry=retry)
        else:
            raise

    status_code_first_digit = request.status_code // 100
    if status_code_first_digit == 2:
        try:
            request_dict = request.json()
            if 'latest_api_version' in request_dict:
                if request_dict['latest_api_version'] > LATEST_API_VERSION:
                    logging.warning('New API version may be available.')
            return request_dict
        except Exception:
            return request.content
    elif status_code_first_digit == 4:
        raise ValueError(request.content)
    elif status_code_first_digit == 5:
        if retry is True:
            logging.warning(request.content)
            logging.warning('Got a 500, retrying in 5 seconds...')
            sleep(5)
            # Try again if we get a 500
            return api_request(url, json_params, retry=retry)
        else:
            raise Exception(request.content)
    else:
        # Not sure why we'd get this.
        request.raise_for_status()
        raise Exception('Stuff broke strangely.')


def normalize_argument(argument):
    """
    Helps normalize arguments from aaargh that may not be what we want.
    """
    if argument == 'False':
        return False
    elif argument == 'True':
        return True
    elif argument == 'None':
        return None
    else:
        return argument


def get_url(api_endpoint, host, target):
    if api_endpoint is None:
        api_endpoint = 'http://{}'.format(host)
    return '{}/v{}/{}'.format(api_endpoint, LATEST_API_VERSION, target)


# FIXME: ordering
@cli.cmd
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--hostaccess', type=bool, default=False)
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--organization', type=str, default=None)
@cli.cmd_arg('--managed', type=bool, default=False)
@cli.cmd_arg('--currency', type=str)
@cli.cmd_arg('--cores', type=int, default=1)
@cli.cmd_arg('--memory', type=int)
@cli.cmd_arg('--disk', type=int)
@cli.cmd_arg('--days', type=int)
@cli.cmd_arg('--bandwidth', type=int)
@cli.cmd_arg('--ipv4')
@cli.cmd_arg('--ipv6')
@cli.cmd_arg('--region', type=str, default=None)
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--refund_address', type=str, default=None)
@cli.cmd_arg('--qemuopts', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=None)
@cli.cmd_arg('--host', type=str, default=None)
@cli.cmd_arg('--ipxescript', type=str, default=None)
@cli.cmd_arg('--operating_system', type=str, default=None)
@cli.cmd_arg('--ssh_key', type=str, default=None)
@cli.cmd_arg('--want_topup', type=bool, default=False)
def launch(machine_id,
           days,
           disk,
           memory,
           ipv4,
           ipv6,
           bandwidth,
           currency,
           region=None,
           ipxescript=None,
           operating_system=None,
           ssh_key=None,
           organization=None,
           refund_address=None,
           cores=1,
           managed=False,
           override_code=None,
           settlement_token=None,
           qemuopts=None,
           hostaccess=False,
           api_endpoint=None,
           host=None,
           want_topup=False,
           retry=False):
    """
    Only ipxescript or operating_system + ssh_key can be None.
    """
    ipv4 = normalize_argument(ipv4)
    ipv6 = normalize_argument(ipv6)
    bandwidth = normalize_argument(bandwidth)

    validate.ipv4(ipv4)
    validate.ipv6(ipv6)
    validate.bandwidth(bandwidth)
    validate.cores(cores)
    validate.disk(disk)
    validate.memory(memory)
    validate.organization(organization)
    validate.machine_id(machine_id)
    validate.ipxescript(ipxescript)
    validate.operating_system(operating_system)
    validate.ssh_key(ssh_key)

    json_params = {'machine_id': machine_id,
                   'days': days,
                   'disk': disk,
                   'memory': memory,
                   'refund_address': refund_address,
                   'cores': cores,
                   'managed': managed,
                   'currency': currency,
                   'region': region,
                   'organization': organization,
                   'bandwidth': bandwidth,
                   'ipv4': ipv4,
                   'ipv6': ipv6,
                   'override_code': override_code,
                   'settlement_token': settlement_token,
                   'qemuopts': qemuopts,
                   'hostaccess': hostaccess,
                   'ipxescript': ipxescript,
                   'operating_system': operating_system,
                   'ssh_key': ssh_key,
                   'want_topup': want_topup,
                   'host': host}

    url = get_url(api_endpoint=api_endpoint, host=host, target='launch')
    return api_request(url=url, json_params=json_params, retry=retry)


@cli.cmd
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--settlement_token', type=str, default=None)
@cli.cmd_arg('--override_code', type=str, default=None)
@cli.cmd_arg('--currency', type=str, default=None)
@cli.cmd_arg('--days', type=int)
@cli.cmd_arg('--refund_address', type=str, default=None)
@cli.cmd_arg('--api_endpoint', type=str, default=None)
@cli.cmd_arg('--host', type=str, default=None)
def topup(machine_id,
          days,
          currency,
          settlement_token=None,
          refund_address=None,
          override_code=None,
          api_endpoint=None,
          host=None,
          retry=False):
    validate.machine_id(machine_id)

    json_params = {'machine_id': machine_id,
                   'days': days,
                   'refund_address': refund_address,
                   'settlement_token': settlement_token,
                   'currency': currency,
                   'host': host,
                   'override_code': override_code}
    url = get_url(api_endpoint=api_endpoint, host=host, target='topup')
    return api_request(url=url, json_params=json_params, retry=retry)


@cli.cmd
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
@cli.cmd_arg('--host', type=str, default=None)
def exists(machine_id, api_endpoint=None, host=None):
    """
    Checks if the VM exists.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='exists')
    get_params = {'machine_id': machine_id, 'host': host}
    output = api_request(url, get_params=get_params)
    return output['result']


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def status(host, machine_id, api_endpoint=None):
    """
    Checks if the VM is started or stopped.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='status')
    get_params = {'machine_id': machine_id, 'host': host}
    output = api_request(url, get_params=get_params)
    return output['result']


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def start(host, machine_id, api_endpoint=None):
    """
    Boots the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='start')
    json_params = {'machine_id': machine_id, 'host': host}
    api_request(url, json_params=json_params)
    return True


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def stop(host, machine_id, api_endpoint=None):
    """
    Immediately kills the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='stop')
    json_params = {'machine_id': machine_id, 'host': host}
    api_request(url, json_params=json_params)
    return True


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def sshhostname(host, machine_id, api_endpoint=None):
    """
    Returns a hostname that we can SSH into to reach
    port 22 on the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='sshhostname')
    get_params = {'machine_id': machine_id, 'host': host}
    return api_request(url, get_params=get_params)


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def info(host, machine_id, api_endpoint=None):
    """
    Returns info about the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target='info')
    get_params = {'machine_id': machine_id, 'host': host}
    return api_request(url, get_params=get_params)


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def ipxescript(host, machine_id, ipxescript=None, api_endpoint=None):
    """
    Trying to make this both useful as a CLI tool and
    as a library. Not really sure how to do that best.
    """
    validate.machine_id(machine_id)

    if ipxescript is None:
        if __name__ == '__main__':
            ipxescript = sys.stdin.read()
        else:
            raise ValueError('ipxescript must be set.')

    url = get_url(api_endpoint=api_endpoint, host=host, target='ipxescript')
    json_params = {'machine_id': machine_id,
                   'host': host,
                   'ipxescript': ipxescript}
    return api_request(url, json_params=json_params)


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
@cli.cmd_arg('bootorder')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def bootorder(host, machine_id, bootorder, api_endpoint=None):
    """
    Updates the boot order for a VM.
    """
    validate.machine_id(machine_id)
    validate.bootorder(bootorder)

    url = get_url(api_endpoint=api_endpoint, host=host, target='ipxescript')
    json_params = {'machine_id': machine_id,
                   'host': host,
                   'bootorder': bootorder}
    return api_request(url, json_params=json_params)


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('--api_endpoint', type=str, default=None)
def host_info(host, api_endpoint=None):
    """
    Returns info about the host.

    FIXME: Returns json for now, should return a dict?
    """
    url = get_url(api_endpoint=api_endpoint, host=host, target='host_info')
    return api_request(url)


@cli.cmd
@cli.cmd_arg('host')
@cli.cmd_arg('machine_id')
def serialconsole(host, machine_id):
    """
    ctrl + \ to quit.
    """
    validate.machine_id(machine_id)

    command = 'serialconsole {}'.format(machine_id)
    ssh.ssh(host, command, interactive=True)
    return True


if __name__ == '__main__':
    output = cli.run()
    if output is True:
        exit(0)
    elif output is False:
        exit(1)
    else:
        print(output)
        exit(0)
