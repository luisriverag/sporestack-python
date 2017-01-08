"""
sporestack.com Python API interface

Released into the public domain.
"""

from collections import namedtuple
from warnings import warn
from base64 import b64encode
import json
import urllib2

import yaml


ENDPOINT = 'http://sporestack.com/node'

# ENDPOINT = 'http://localhost:8082/node'

TIMEOUT = 60


def node(days,
         unique,
         sshkey=None,
         cloudinit=None,
         startupscript=None,
         osid=None,
         dcid=None,
         flavor=None,
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
        pre_data['sshkey'] = sshkey
    if startupscript is not None:
        pre_data['startupscript'] = startupscript
    if osid is not None:
        pre_data['osid'] = osid
    if dcid is not None:
        pre_data['dcid'] = dcid
    if flavor is not None:
        pre_data['flavor'] = flavor

    post_data = json.dumps(pre_data)
    try:
        http_return = urllib2.urlopen(endpoint,
                                      data=post_data,
                                      timeout=TIMEOUT)
    except urllib2.HTTPError as http_error:
        if http_error.code == 400:
            # Throw exception with output from endpoint..
            raise Exception(http_error.read())
        else:
            raise
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
        return node
    else:
        raise Exception('Fatal issue with sporestack.')
