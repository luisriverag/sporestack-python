#!/usr/bin/python3

import logging
import sys
import os
from time import sleep

import requests

from . import validate

LATEST_API_VERSION = 2

GET_TIMEOUT = 60
POST_TIMEOUT = 90
USE_TOR_PROXY = "auto"
TOR_PROXY = "socks5h://127.0.0.1:9050"
# For requests module
TOR_PROXY_REQUESTS = {"http": TOR_PROXY, "https": TOR_PROXY}


def validate_use_tor_proxy(use_tor_proxy):
    if isinstance(use_tor_proxy, bool):
        return True
    if isinstance(use_tor_proxy, str):
        if use_tor_proxy == "auto":
            return True

    raise ValueError('use_tor_proxy must be True, False, or "auto"')


def is_onion_url(url):
    """
    returns True/False depending on if a URL looks like a Tor hidden service
    (.onion) or not.
    This is designed to false as non-onion just to be on the safe-ish side,
    depending on your view point. It requires URLs like: http://domain.tld/,
    not http://domain.tld or domain.tld/.

    This can be optimized a lot.
    """
    try:
        url_parts = url.split("/")
        domain = url_parts[2]
        tld = domain.split(".")[-1]
        if tld == "onion":
            return True
    except Exception:
        pass
    return False


def api_request(
    url, json_params=None, get_params=None, retry=False, use_tor_proxy=USE_TOR_PROXY
):
    validate_use_tor_proxy(use_tor_proxy)

    proxies = {}
    if use_tor_proxy is True:
        proxies = TOR_PROXY_REQUESTS
    elif use_tor_proxy == "auto":
        if is_onion_url(url) is True:
            msg = 'use_tor_proxy is "auto" and we have a .onion url, '
            msg += "using local Tor SOCKS proxy."
            logging.debug(msg)
            proxies = TOR_PROXY_REQUESTS

    try:
        if json_params is None:
            request = requests.get(
                url, params=get_params, timeout=GET_TIMEOUT, proxies=proxies
            )
        else:
            request = requests.post(
                url, json=json_params, timeout=POST_TIMEOUT, proxies=proxies
            )
    except Exception as e:
        if retry is True:
            logging.warning("Got an error, but retrying: {}".format(e))
            sleep(5)
            # Try again.
            return api_request(
                url,
                json_params=json_params,
                get_params=get_params,
                retry=retry,
                use_tor_proxy=use_tor_proxy,
            )
        else:
            raise

    status_code_first_digit = request.status_code // 100
    if status_code_first_digit == 2:
        try:
            request_dict = request.json()
            if "latest_api_version" in request_dict:
                if request_dict["latest_api_version"] > LATEST_API_VERSION:
                    logging.warning("New API version may be available.")
            return request_dict
        except Exception:
            return request.content
    elif status_code_first_digit == 4:
        if request.status_code == 415:
            raise NotImplementedError(request.content.decode("utf-8"))
        else:
            logging.debug("Status code: {}".format(request.status_code))
            raise ValueError(request.content.decode("utf-8"))
    elif status_code_first_digit == 5:
        if retry is True:
            logging.warning(request.content.decode("utf-8"))
            logging.warning("Got a 500, retrying in 5 seconds...")
            sleep(5)
            # Try again if we get a 500
            return api_request(
                url,
                json_params=json_params,
                get_params=get_params,
                retry=retry,
                use_tor_proxy=use_tor_proxy,
            )
        else:
            raise Exception(str(request.content))
    else:
        # Not sure why we'd get this.
        request.raise_for_status()
        raise Exception("Stuff broke strangely.")


def normalize_argument(argument):
    """
    Helps normalize arguments from aaargh that may not be what we want.
    """
    if argument == "False":
        return False
    elif argument == "True":
        return True
    elif argument == "None":
        return None
    else:
        return argument


def get_url(api_endpoint, host, target):
    """
    Has nothing to do with GET requests.
    """
    if api_endpoint is None:
        api_endpoint = "http://{}".format(host)
    return "{}/v{}/{}".format(api_endpoint, LATEST_API_VERSION, target)


def launch(
    machine_id,
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
    cores=1,
    managed=False,
    override_code=None,
    settlement_token=None,
    qemuopts=None,
    hostaccess=False,
    api_endpoint=None,
    host=None,
    want_topup=False,
    retry=False,
    affiliate_amount=None,
    affiliate_token=None,
):
    """
    Only ipxescript or operating_system + ssh_key can be None.
    """
    ipv4 = normalize_argument(ipv4)
    ipv6 = normalize_argument(ipv6)
    bandwidth = normalize_argument(bandwidth)

    validate.currency(currency)
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
    validate.affiliate_amount(affiliate_amount)

    json_params = {
        "machine_id": machine_id,
        "days": days,
        "disk": disk,
        "memory": memory,
        "cores": cores,
        "managed": managed,
        "currency": currency,
        "region": region,
        "organization": organization,
        "bandwidth": bandwidth,
        "ipv4": ipv4,
        "ipv6": ipv6,
        "override_code": override_code,
        "settlement_token": settlement_token,
        "qemuopts": qemuopts,
        "hostaccess": hostaccess,
        "ipxescript": ipxescript,
        "operating_system": operating_system,
        "ssh_key": ssh_key,
        "want_topup": want_topup,
        "host": host,
        "affiliate_amount": affiliate_amount,
        "affiliate_token": affiliate_token,
    }

    url = get_url(api_endpoint=api_endpoint, host=host, target="launch")
    return api_request(url=url, json_params=json_params, retry=retry)


def topup(
    machine_id,
    days,
    currency,
    settlement_token=None,
    override_code=None,
    api_endpoint=None,
    host=None,
    retry=False,
    affiliate_amount=None,
    affiliate_token=None,
):
    validate.machine_id(machine_id)
    validate.currency(currency)
    validate.affiliate_amount(affiliate_amount)

    json_params = {
        "machine_id": machine_id,
        "days": days,
        "settlement_token": settlement_token,
        "currency": currency,
        "host": host,
        "override_code": override_code,
        "affiliate_amount": affiliate_amount,
        "affiliate_token": affiliate_token,
    }
    url = get_url(api_endpoint=api_endpoint, host=host, target="topup")
    return api_request(url=url, json_params=json_params, retry=retry)


def start(host, machine_id, api_endpoint=None):
    """
    Boots the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target="start")
    json_params = {"machine_id": machine_id, "host": host}
    api_request(url, json_params=json_params)
    return True


def stop(host, machine_id, api_endpoint=None):
    """
    Immediately kills the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target="stop")
    json_params = {"machine_id": machine_id, "host": host}
    api_request(url, json_params=json_params)
    return True


def delete(host, machine_id, api_endpoint=None):
    """
    Immediately deletes the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target="delete")
    json_params = {"machine_id": machine_id, "host": host}
    api_request(url, json_params=json_params)
    return True


def sshhostname(host, machine_id, api_endpoint=None):
    """
    Returns a hostname that we can SSH into to reach
    port 22 on the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target="sshhostname")
    get_params = {"machine_id": machine_id, "host": host}
    return api_request(url, get_params=get_params)


def info(host, machine_id, api_endpoint=None):
    """
    Returns info about the VM.
    """
    validate.machine_id(machine_id)

    url = get_url(api_endpoint=api_endpoint, host=host, target="info")
    get_params = {"machine_id": machine_id, "host": host}
    return api_request(url, get_params=get_params)


def ipxescript(host, machine_id, ipxescript=None, api_endpoint=None):
    """
    Trying to make this both useful as a CLI tool and
    as a library. Not really sure how to do that best.
    """
    validate.machine_id(machine_id)

    if ipxescript is None:
        if __name__ == "__main__":
            ipxescript = sys.stdin.read()
        else:
            raise ValueError("ipxescript must be set.")

    url = get_url(api_endpoint=api_endpoint, host=host, target="ipxescript")
    json_params = {"machine_id": machine_id, "host": host, "ipxescript": ipxescript}
    return api_request(url, json_params=json_params)


def bootorder(host, machine_id, bootorder, api_endpoint=None):
    """
    Updates the boot order for a VM.
    """
    validate.machine_id(machine_id)
    validate.bootorder(bootorder)

    url = get_url(api_endpoint=api_endpoint, host=host, target="ipxescript")
    json_params = {"machine_id": machine_id, "host": host, "bootorder": bootorder}
    return api_request(url, json_params=json_params)


def host_info(host, api_endpoint=None):
    """
    Returns info about the host.
    """
    url = get_url(api_endpoint=api_endpoint, host=host, target="host_info")
    return api_request(url)


def serialconsole(host, machine_id):
    """
    This needs to be adjusted to use a Tor socks proxy of the host is a .onion.
    """
    validate.machine_id(machine_id)

    command = "/usr/bin/ssh"
    arguments = []
    arguments.append(command)
    arguments.append("-t")
    arguments.append("vmmanagement@{}".format(host))
    arguments.append("-p")
    arguments.append("1060")
    arguments.append("serialconsole {}".format(machine_id))
    logging.info(command, arguments)
    os.execv(command, arguments)


def settlement_token_enable(
    settlement_token, cents, currency, api_endpoint=None, retry=False
):
    validate.settlement_token(settlement_token)
    validate.cents(cents)
    validate.currency(currency)

    json_params = {
        "settlement_token": settlement_token,
        "cents": cents,
        "currency": currency,
    }
    url = api_endpoint + "/settlement/enable"
    return api_request(url=url, json_params=json_params, retry=retry)


def settlement_token_add(
    settlement_token, cents, currency, api_endpoint=None, retry=False
):
    validate.settlement_token(settlement_token)
    validate.cents(cents)
    validate.currency(currency)

    json_params = {
        "settlement_token": settlement_token,
        "cents": cents,
        "currency": currency,
    }
    url = api_endpoint + "/settlement/add"
    return api_request(url=url, json_params=json_params, retry=retry)


def settlement_token_balance(settlement_token, api_endpoint=None, retry=False):
    validate.settlement_token(settlement_token)

    get_params = {"settlement_token": settlement_token}
    url = api_endpoint + "/settlement/balance"
    return api_request(url=url, get_params=get_params, retry=retry)
