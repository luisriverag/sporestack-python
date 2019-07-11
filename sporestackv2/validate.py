"""
Validates arguments.

All functions return True if valid, or raise an exception.
"""

import string

from sshpubkeys import SSHKey


def machine_id(machine_id):
    """
    Validates the machine_id
    Must be a 64 byte lowercase hex string.
    A sha256sum, in effect.
    """
    if not isinstance(machine_id, str):
        raise TypeError('machine_id must be a string.')
    if len(machine_id) != 64:
        raise ValueError('machine_id must be exactly 64 bytes/characters.')
    for letter in machine_id:
        if letter not in '0123456789abcdef':
            raise ValueError('machine_id must be only 0-9, a-f (lowercase)')
    return True


def operating_system(operating_system):
    """
    Validates an operating_system argument.
    """
    if operating_system is None:
        return True
    if not isinstance(operating_system, str):
        raise TypeError('operating_system must be null or a string.')
    if len(operating_system) < 1:
        raise ValueError('operating_system must have at least one letter.')
    if len(operating_system) > 16:
        raise ValueError('operating_system must have 16 letters or less.')
    for character in operating_system:
        if character not in string.ascii_lowercase + string.digits + "-":
            msg = 'operating_system must only contain a-z, digits, -'
            raise ValueError(msg)

    return True


def ssh_key(ssh_key):
    """
    Validates an ssh_key argument.
    """
    if ssh_key is None:
        return True
    if not isinstance(ssh_key, str):
        raise TypeError('ssh_key must be null or a string.')

    ssh_key_object = SSHKey(ssh_key,
                            skip_option_parsing=True,
                            disallow_options=True)
    try:
        ssh_key_object.parse()
    except Exception as e:
        raise ValueError("Invalid SSH key: {}".format(e))

    return True


def days(days, zero_allowed=False):
    """
    Makes sure our argument is valid.
    0-28
    Keep in mind that 0 days implies no expiration and is
    only allowed if override_code is set.

    0 is invalid unless zero_allowed is True.
    """
    if not isinstance(days, int):
        raise TypeError('days must be an integer type')

    if zero_allowed is True:
        minimum_days = 0
    else:
        minimum_days = 1

    if days < minimum_days or days > 28:
        raise ValueError('days must be {}-28'.format(minimum_days))

    return True


def organization(organization):
    if organization is None:
        return True
    if not isinstance(organization, str):
        raise TypeError('organization must be string.')
    if len(organization) < 1:
        raise ValueError('organization must have at least one letter.')
    if len(organization) > 16:
        raise ValueError('organization must have 16 letters or less.')
    for character in organization:
        if character not in string.ascii_letters:
            raise ValueError('organization must only contain a-z, A-Z')
    return True


def unsigned_int(variable):
    """
    Make sure variable is an unsigned int.
    """
    if not isinstance(variable, int):
        return False
    if variable < 0:
        return False
    return True


def disk(disk):
    """
    Makes sure disk is valid.

    0 is valid, means no disk.
    """
    if not unsigned_int(disk):
        raise TypeError('disk must be an unsigned integer.')
    return True


def memory(memory):
    """
    Makes sure memory is valid.
    """
    if not unsigned_int(memory):
        raise TypeError('memory must be an unsigned integer.')
    if memory == 0:
        raise ValueError('0 not acceptable for memory')
    return True


def expiration(expiration):
    """
    Makes sure expiration is valid.
    """
    if not unsigned_int(expiration):
        raise TypeError('expiration must be an unsigned integer.')
    return True


def cores(cores):
    """
    Makes sure cores is valid.
    """
    if not unsigned_int(cores):
        raise TypeError('cores must be an unsigned integer.')
    return True


def qemuopts(qemuopts):
    """
    Makes sure qemuopts is valid.
    """
    if qemuopts is None:
        return True
    if not isinstance(qemuopts, str):
        raise TypeError('qemuopts must be none or str.')
    return True


def managed(managed):
    """
    Makes sure managed is valid.
    """
    if not isinstance(managed, bool):
        raise TypeError('managed must be a boolean.')
    return True


def hostaccess(hostaccess):
    """
    Makes sure hostaccess is valid.
    """
    if not isinstance(hostaccess, bool):
        raise TypeError('hostaccess must be a boolean.')
    return True


def currency(currency):
    """
    Makes sure currency is valid.
    """
    if currency is None:
        return True
    if not isinstance(currency, str):
        raise TypeError('currency must be None or str.')
    return True


def refund_address(refund_address):
    """
    Makes sure refund_address is valid.

    Currently not implemented.
    """
    if refund_address is None:
        return True
    if not isinstance(refund_address, str):
        raise TypeError('refund_address must be none or str.')
    return True


def bandwidth(bandwidth):
    """
    Bandwidth is in gigabytes per day.
    -1 is "unlimited".
    0 means no bandwidth. Only valid if ipv4 and ipv6 are False.
    """
    if isinstance(bandwidth, int):
        if bandwidth >= -1:
            return True
        else:
            raise ValueError('bandwidth can be no lower than -1.')
    else:
        raise TypeError('bandwidth must be integer.')


def _ip(ip, ip_type, cidr):
    """
    Helper for ipv4 and ipv6

    """
    # bool is int in Python 3, so have to test for bool first...
    if ip is False:
        return True

    if not isinstance(ip, str):
        raise TypeError('ipv4 must be false or string.')
    elif ip == cidr:
        return True
    elif ip == 'nat':
        return True
    elif ip == 'tor':
        return True
    else:
        raise ValueError('{} must be one of: False|{}'.format(ip_type, cidr))


def ipv4(ipv4):
    return _ip(ipv4, 'ipv4', '/32')


def ipv6(ipv6):
    return _ip(ipv6, 'ipv6', '/128')


# further calls are for validating compatibilities between
# argument cominations.

def further_ipv4_ipv6(ipv4, ipv6):
    """
    More validation with the combination of ipv4 and ipv6 options.

    We don't support mixed nat/tor modes, so this handles that.
    """
    message = 'ipv4 and ipv6 must be the same if either is tor or nat.'

    if ipv4 in ['tor', 'nat'] or ipv6 in ['tor', 'nat']:
        if ipv4 != ipv6:
            raise ValueError(message)
    return True


def ipxescript(ipxescript):
    if ipxescript is None:
        return True
    if not isinstance(ipxescript, str):
        raise TypeError('ipxescript must be a string or null.')
    if len(ipxescript) == 0:
        raise ValueError('ipxescript must be more than zero bytes long.')
    if len(ipxescript) > 4000:
        raise ValueError('ipxescript must be less than 4,000 bytes long.')
    for letter in ipxescript:
        if letter not in string.printable:
            raise ValueError('ipxescript must only contain ascii characters.')
    return True


def region(region):
    if region is None:
        return True
    if not isinstance(region, str):
        raise TypeError('region must be a string or null.')
    if len(region) == 0:
        raise ValueError('region must be more than zero bytes long.')
    if len(region) > 200:
        raise ValueError('region must be less than 200 bytes long.')
    for letter in region:
        if letter not in string.printable:
            raise ValueError('region must only contain ascii characters.')
    return True


# Currently unused.
def address(currency, address):
    # This is incomplete and unused. FIXME
    return True


def must_have_exact_keys(dictionary, list_of_keys):
    if not isinstance(dictionary, dict):
        raise TypeError('dictionary must be dict')
    has_items = []
    for item in list_of_keys:
        if item not in dictionary:
            raise ValueError('{} missing.'.format(item))
        else:
            has_items.append(item)

    if len(list_of_keys) != len(dictionary):
        raise ValueError('Extraneous keys')

    return True


def affiliate(affiliate):
    our_keys = ['currencies', 'per_day_cents', 'launch_cents']
    our_currency_keys = ['btc', 'bch', 'bsv']
    if affiliate is None:
        return True
    if not isinstance(affiliate, dict):
        raise TypeError('affiliate must be dict or None')
    must_have_exact_keys(affiliate, our_keys)
    if not isinstance(affiliate["currencies"], dict):
        raise ValueError('affiliate["currencies"] must be dict')
    must_have_exact_keys(affiliate["currencies"], our_currency_keys)
    for our_currency in our_currency_keys:
        currency(our_currency)
        address(our_currency, affiliate["currencies"][our_currency])
    unsigned_int(affiliate["per_day_cents"])
    unsigned_int(affiliate["launch_cents"])
    return True
#
