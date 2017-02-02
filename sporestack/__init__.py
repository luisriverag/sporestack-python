"""
sporestack.com Python API interface

Released into the public domain.
"""

from collections import namedtuple
from warnings import warn
from base64 import b64encode
import json

# Python 2 backwards compatibility.
try:
    from urllib.request import urlopen, HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError

import yaml


ENDPOINT = 'https://sporestack.com'

TIMEOUT = 60
OPTIONS_TIMEOUT = 10


def node_options():
    """
    Returns a dict of options for osid, dcid, and flavor.
    """
    http_return = urlopen(ENDPOINT + '/node/options',
                          timeout=OPTIONS_TIMEOUT)
    if http_return.getcode() != 200:
        raise Exception('SporeStack /node/options did not return HTTP 200.')
    return yaml.safe_load(http_return.read())


def node_get_launch_profile(profile):
    """
    Returns dict of launch instance.
    Use 'index' if you want a list of all available.
    https://sporestack.com/launch
    """
    url = '{}/launch/{}.json'.format(ENDPOINT, profile)
    http_return = urlopen(url,
                          timeout=OPTIONS_TIMEOUT)
    if http_return.getcode() != 200:
        raise Exception('{} did not return HTTP 200.'.format(url))
    return yaml.safe_load(http_return.read())


def node(days,
         unique,
         sshkey=None,
         cloudinit=None,
         startupscript=None,
         osid=None,
         dcid=None,
         flavor=None,
         paycode=None,
         endpoint=ENDPOINT):
    """
    Returns a node

    Returns:
    node.payment_status
    node.end_of_life
    node.ip6
    node.ip4
    """

    pre_data = {'days': days,
                'unique': unique}

    # There must be a better way to do this...
    if cloudinit is not None:
        b64_cloudinit = b64encode(cloudinit)
        pre_data['cloudinit'] = b64_cloudinit
    if sshkey is not None:
        # Strip comment field off of SSH key before we send it to SporeStack,
        # in case it has any.
        sshkey_prefix = sshkey.split(' ')[0]
        sshkey_key = sshkey.split(' ')[1]
        commentless_key = sshkey_prefix + ' ' + sshkey_key
        sshkey = commentless_key
        pre_data['sshkey'] = sshkey
    if startupscript is not None:
        pre_data['startupscript'] = startupscript
    if osid is not None:
        pre_data['osid'] = osid
    if dcid is not None:
        pre_data['dcid'] = dcid
    if flavor is not None:
        pre_data['flavor'] = flavor
    if paycode is not None:
        pre_data['paycode'] = paycode
    if endpoint is None:
        endpoint = ENDPOINT

    # Python 2 and 3 compatibility
    try:
        post_data = bytes(json.dumps(pre_data), 'utf-8')
    except:
        post_data = json.dumps(pre_data)
    try:
        http_return = urlopen(endpoint + '/node',
                              data=post_data,
                              timeout=TIMEOUT)
    except HTTPError as http_error:
        if http_error.code != 200:
            # Throw exception with output from endpoint..
            raise Exception(http_error.read())
            return False
        else:
            raise HTTPError
            return False
    except:
        # Ugly hack.
        raise HTTPError
        return False
    if http_return.getcode() == 200:
        data = yaml.safe_load(http_return.read())
        if 'deprecated' in data:
            if data['deprecated'] is not False:
                warn(str(data['deprecated']), DeprecationWarning)
        node = namedtuple('node',
                          data.keys())
        node.end_of_life = data['end_of_life']
        node.payment_status = data['payment_status']
        node.creation_status = data['creation_status']
        node.address = data['address']
        node.satoshis = data['satoshis']
        node.ip4 = data['ip4']
        node.ip6 = data['ip6']
        node.hostname = data['hostname']
        return node
    else:
        raise Exception('Fatal issue with sporestack.')
