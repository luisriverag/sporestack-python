from . import api_client

import pytest


def test_validate_validate_use_tor_proxy():
    assert api_client.validate_use_tor_proxy(True) is True
    assert api_client.validate_use_tor_proxy(False) is True
    assert api_client.validate_use_tor_proxy('auto') is True
    with pytest.raises(ValueError):
        api_client.validate_use_tor_proxy('some string')
    with pytest.raises(ValueError):
        api_client.validate_use_tor_proxy(1)
    with pytest.raises(ValueError):
        api_client.validate_use_tor_proxy(0)


def test_is_onion_url():
    onion_url = 'http://spore64i5sofqlfz5gq2ju4msgzojjwifls7'
    onion_url += 'rok2cti624zyq3fcelad.onion/v2/'
    assert api_client.is_onion_url(onion_url) is True
    # This is a good, unusual test.
    onion_url = 'https://www.facebookcorewwwi.onion/'
    assert api_client.is_onion_url(onion_url) is True
    assert api_client.is_onion_url('http://domain.com') is False
    assert api_client.is_onion_url('domain.com') is False
    assert api_client.is_onion_url('http://onion.domain.com/.onion/') is False
    assert api_client.is_onion_url('http://me.me/file.onion/') is False
    assert api_client.is_onion_url('http://me.me/file.onion') is False
