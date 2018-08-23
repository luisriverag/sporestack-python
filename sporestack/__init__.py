"""
sporestack.com Python API interface

Released into the public domain.
"""

from collections import namedtuple
from warnings import warn
from base64 import b64encode

import requests

__version__ = '0.9.0'

DEFAULT_ENDPOINT = 'https://sporestack.com'


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
    except Exception:
        return b64encode(data)


def _validate_request(request):
    """
    Returns True if 2XX status code,
    Raises ValueError with body if 4XX,
    Raises Except with body if something else.
    """
    try:
        request.raise_for_status()
    except Exception:
        if str(request.status_code)[0] == '4':
            raise ValueError(request.content)
        else:
            code_and_body = '{}: {}'.format(request.status_code,
                                            request.content)
            raise Exception(code_and_body)
    return True


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
        request = requests.get(url=self.endpoint + '/node/options')
        _validate_request(request)
        return request.json()

    def node_get_launch_profile(self, profile):
        """
        Returns dict of launch instance.
        https://sporestack.com/launch
        """
        url = '{}/launch/{}.json'.format(self.endpoint, profile)
        request = requests.get(url)
        _validate_request(request)
        return request.json()

    def node_get_launch_profiles(self):
        """
        Returns a dict of launch profiles.
        """
        return self.node_get_launch_profile('index')

    def node(self,
             days,
             uuid,
             currency='bch',
             sshkey=None,
             cloudinit=None,
             startupscript=None,
             ipxe=False,
             ipxe_chain_url=None,
             osid=None,
             dcid=None,
             flavor=None,
             settlement_token=None):
        """
        Returns a node

        Returns:
        node.payment_status
        node.end_of_life
        node.ip6
        node.ip4
        node.satoshis
        node.address
        """

        # Hrmph.
        if ipxe_chain_url is not None:
            ipxe = True

        post_data = {'days': days,
                     'ipxe': ipxe,
                     'ipxe_chain_url': ipxe_chain_url,
                     'osid': osid,
                     'dcid': dcid,
                     'flavor': flavor,
                     'startupscript': startupscript,
                     'sshkey': _sshkey_strip(sshkey),
                     'cloudinit': _b64(cloudinit),
                     'uuid': uuid,
                     'currency': currency,
                     'settlement_token': settlement_token}

        request = requests.post(self.endpoint + '/node',
                                json=post_data)

        _validate_request(request)

        data = request.json()
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

    def node_topup(self,
                   days,
                   uuid,
                   currency='bch',
                   settlement_token=None):
        """
        Lets you raise the end_of_life on a node.

        Returns:
        node.payment_status
        node.end_of_life
        node.satoshis
        node.address

        Should pay in 100 seconds or less! Satoshi padding changes.
        """

        post_data = {'days': days,
                     'uuid': uuid,
                     'currency': currency,
                     'settlement_token': settlement_token}

        request = requests.post(self.endpoint + '/node/topup',
                                json=post_data)

        _validate_request(request)

        data = request.json()
        if 'deprecated' in data and data['deprecated'] is not False:
            warn(str(data['deprecated']), DeprecationWarning)
        # Iffy on this.
        node = namedtuple('node',
                          data.keys())
        node.end_of_life = data['end_of_life']
        node.payment_status = data['payment_status']
        node.address = data['address']
        node.satoshis = data['satoshis']

        return node
