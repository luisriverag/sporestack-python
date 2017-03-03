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


DEFAULT_ENDPOINT = 'https://sporestack.com'

TIMEOUT = 60
OPTIONS_TIMEOUT = 10


def _sshkey_strip(sshkey):
    """
    Strip comment field off of SSH key before we send it to SporeStack,
    in case it has any.
    """
    if sshkey is None:
        return None
    sshkey_prefix = sshkey.split(' ')[0]
    sshkey_key = sshkey.split(' ')[1]
    commentless_key = sshkey_prefix + ' ' + sshkey_key
    return commentless_key


def _b64(data):
    """
    Returns base64 version of data.

    try/except is for Python 3/2 compatibility.
    """
    if data is None:
        return None
    try:
        return b64encode(bytes(data, 'utf-8')).decode('utf-8')
    except:
        return b64encode(data)


class SporeStack():
    """
    SporeStack class.
    """
    def __init__(self, endpoint=DEFAULT_ENDPOINT):
        self.endpoint = endpoint

    def node_options(self):
        """
        Returns a dict of options for osid, dcid, and flavor.
        """
        http_return = urlopen(self.endpoint + '/node/options',
                              timeout=OPTIONS_TIMEOUT)
        if http_return.getcode() != 200:
            msg = 'SporeStack /node/options did not return HTTP 200.'
            raise Exception(msg)
        return yaml.safe_load(http_return.read())

    def node_get_launch_profile(self, profile):
        """
        Returns dict of launch instance.
        https://sporestack.com/launch
        """
        url = '{}/launch/{}.json'.format(self.endpoint, profile)
        http_return = urlopen(url,
                              timeout=OPTIONS_TIMEOUT)
        if http_return.getcode() != 200:
            raise Exception('{} did not return HTTP 200.'.format(url))
        return yaml.safe_load(http_return.read())

    def node_get_launch_profiles(self):
        """
        Returns a dict of launch profiles.
        """
        return self.node_get_launch_profile('index')

    def node(self,
             days,
             uuid,
             sshkey=None,
             cloudinit=None,
             startupscript=None,
             ipxe=False,
             ipxe_chain_url=None,
             osid=None,
             dcid=None,
             flavor=None,
             paycode=None):
        """
        Returns a node

        Returns:
        node.payment_status
        node.end_of_life
        node.ip6
        node.ip4
        node.satoshis
        node.address

        Must pay in 100 seconds or less! Satoshi padding changes.
        """

        # Hrmph.
        if ipxe_chain_url is not None:
            ipxe = True

        pre_data = {'days': days,
                    'ipxe': ipxe,
                    'ipxe_chain_url': ipxe_chain_url,
                    'osid': osid,
                    'dcid': dcid,
                    'flavor': flavor,
                    'paycode': paycode,
                    'startupscript': startupscript,
                    'sshkey': _sshkey_strip(sshkey),
                    'cloudinit': _b64(cloudinit),
                    'uuid': uuid}

        # Python 3 and 2 compatibility
        try:
            post_data = bytes(json.dumps(pre_data), 'utf-8')
        except:
            post_data = json.dumps(pre_data)

        try:
            http_return = urlopen(self.endpoint + '/node',
                                  data=post_data,
                                  timeout=TIMEOUT)
        except HTTPError as http_error:
            # Throw exception with output from endpoint..
            # This needs another name.
            raise ValueError(http_error.read())

        if http_return.getcode() == 200:
            data = yaml.safe_load(http_return.read())
            if 'deprecated' in data and data['deprecated'] is not False:
                warn(str(data['deprecated']), DeprecationWarning)
            # Iffy on this.
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
            node.kvm_url = data['kvm_url']

            return node
        else:
            raise Exception('Fatal issue with sporestack.')
