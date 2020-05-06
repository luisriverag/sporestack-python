"""
Various utility functions for SporeStack.
"""

from . import validate


def payment_to_uri(address, currency, amount):
    """
    payment_to_uri: Converts address, currency, and amount (in Satoshis)
    to a payment URI.

    amount is called amount because we may add a currency that doesn't have
    'satoshis' one day. This is meant to be normalizing.

    This does *not* validate address.
    """
    if not isinstance(address, str):
        raise TypeError('address must be string.')
    if not isinstance(currency, str):
        raise TypeError('currency must be string.')
    if not validate.unsigned_int(amount):
        raise TypeError('amount must be unsigned int.')

    if len(address) == 0:
        raise ValueError('address cannot be 0 length.')

    btc_decimal_amount = "{0:.8f}".format(amount * 0.00000001)
    if currency == 'btc':
        uri = 'bitcoin:{}?amount={}'.format(address, btc_decimal_amount)
    elif currency == 'bch':
        # This does not support "legacy" base58 addresses for Bitcoin Cash.
        uri = '{}?amount={}'.format(address, btc_decimal_amount)
    elif currency == 'bsv':
        # This does not support "legacy" cashaddr addresses for Bitcoin SV.
        uri = 'bitcoin:{}?amount={}'.format(address, btc_decimal_amount)
    elif currency == 'xmr':
        xmr_decimal_amount = "{0:.12f}".format(amount * 0.000000000001)
        uri = 'monero:{}?tx_amount={}'.format(address, xmr_decimal_amount)
    else:
        raise ValueError('Currency must be one of: btc, bch, bsv, xmr')

    return uri


def cents_to_usd(cents):
    """
    cents_to_usd: Convert cents to USD string.
    """
    if not validate.unsigned_int(cents):
        raise TypeError('cents must be unsigned int.')
    return '${:,.2f}'.format(cents * 0.01)
