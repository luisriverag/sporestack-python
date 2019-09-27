from . import utilities

import pytest


def test_payment_to_uri():
    address = "1xm4vFerV3pSgvBFkyzLgT1Ew3HQYrS1V"
    currency = "btc"
    amount = 12345678
    output = utilities.payment_to_uri(address=address,
                                      currency=currency,
                                      amount=amount)
    expected = "bitcoin:1xm4vFerV3pSgvBFkyzLgT1Ew3HQYrS1V?amount=0.12345678"
    assert output == expected

    address = "1xm4vFerV3pSgvBFkyzLgT1Ew3HQYrS1V"
    currency = "bsv"
    amount = 200000000
    output = utilities.payment_to_uri(address=address,
                                      currency=currency,
                                      amount=amount)
    expected = "bitcoin:1xm4vFerV3pSgvBFkyzLgT1Ew3HQYrS1V?amount=2.00000000"
    assert output == expected

    address = "bitcoincash:qq9gh20y2vur63tpe0xa5dh90zwzsuxagyhp7pfuv3"
    currency = "bch"
    amount = 1000001
    output = utilities.payment_to_uri(address=address,
                                      currency=currency,
                                      amount=amount)
    expected = address + "?amount=0.01000001"
    assert output == expected

    address = "85rBW1Afx7TSteLwk4xfXcH57v7JzgsnRMi1cJugQatXTNB1gqbf"
    address += "vcP47iPXXU1yqgJofrShLzKnBYBmMCTSSw2h1iaQs8h"
    currency = "xmr"
    amount = 1000001
    output = utilities.payment_to_uri(address=address,
                                      currency=currency,
                                      amount=amount)
    # piconeros are smaller than Satoshis.
    expected = "monero:" + address + "?tx_amount=0.000001000001"
    assert output == expected

    # Negative tests.
    with pytest.raises(ValueError):
        utilities.payment_to_uri(address=address,
                                 currency="xxx",
                                 amount=amount)
    with pytest.raises(TypeError):
        utilities.payment_to_uri(address=address,
                                 currency=currency,
                                 amount="100")


def test_cents_to_usd():
    output = utilities.cents_to_usd(1)
    assert output == "$0.01"
    output = utilities.cents_to_usd(10)
    assert output == "$0.10"
    output = utilities.cents_to_usd(100)
    assert output == "$1.00"
    output = utilities.cents_to_usd(123456)
    assert output == "$1,234.56"
    with pytest.raises(TypeError):
        utilities.cents_to_usd(None)
    with pytest.raises(TypeError):
        utilities.cents_to_usd(-1)
    with pytest.raises(TypeError):
        utilities.cents_to_usd("10")
