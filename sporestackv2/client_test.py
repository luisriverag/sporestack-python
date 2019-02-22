from . import client


def test_payment_uri():
    uri = 'bitcoin:1Az?amount=0.00001000'
    assert client.payment_uri('btc', '1Az', 1000) == uri
    uri = 'bitcoincash:aaaa?amount=0.00001000'
    assert client.payment_uri('bch', 'bitcoincash:aaaa', 1000) == uri
    assert client.payment_uri('bch', 'aaaa', 1000) == uri


def test_random_machine_id():
    assert len(client.random_machine_id()) == 64


def test_api_endpoint_to_host():
    assert client.api_endpoint_to_host('http://foo.bar') == 'foo.bar'
    assert client.api_endpoint_to_host('https://foo.bar') == 'foo.bar'
