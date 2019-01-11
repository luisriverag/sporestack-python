import sporestack.cli as cli


def test_payment_uri():
    assert cli.payment_uri('btc', '13i2BNi49URkZXgVwkoA7nKT1TSE97uWyY', 10000) == 'bitcoin:13i2BNi49URkZXgVwkoA7nKT1TSE97uWyY?amount=0.00010000'
    assert cli.payment_uri('bch', '13i2BNi49URkZXgVwkoA7nKT1TSE97uWyY', 10000) == 'bitcoincash:13i2BNi49URkZXgVwkoA7nKT1TSE97uWyY?amount=0.00010000'
    assert cli.payment_uri('bch', 'bitcoincash:qqwmyjjplsqwltkcgyeagqpjspaaksz3qggnfug7gy', 10000) == 'bitcoincash:qqwmyjjplsqwltkcgyeagqpjspaaksz3qggnfug7gy?amount=0.00010000'
