from uuid import uuid4 as random_uuid

import sporestack


SporeStack = sporestack.SporeStack()


def test__sshkey_strip():
    full_sshkey = 'ssh-rsa AAAA foo@foo'
    correct_sshkey = 'ssh-rsa AAAA'
    assert sporestack._sshkey_strip(full_sshkey) == correct_sshkey
    assert sporestack._sshkey_strip(correct_sshkey) == correct_sshkey

def test_node_options():
    options = SporeStack.node_options()
    assert 'FreeBSD' in str(options)
    assert 'Windows' not in str(options)

def test_node_get_launch_profile():
    vpn = SporeStack.node_get_launch_profile('vpn')
    assert 'openvpn' in str(vpn)

def test_node():
    uuid = str(random_uuid())
    node = SporeStack.node(days=1, unique=uuid, cloudinit='#!/bin/true')
    assert node.satoshis > 20000
    assert node.satoshis < 55000
