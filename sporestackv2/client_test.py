from . import client


def test_payment_uri():
    uri = 'bitcoin:1Az?amount=0.00001000'
    assert client.payment_uri('btc', '1Az', 1000) == uri
    uri = 'bitcoincash:aaaa?amount=0.00001000'
    assert client.payment_uri('bch', 'bitcoincash:aaaa', 1000) == uri
    assert client.payment_uri('bch', 'aaaa', 1000) == uri
