import string

import pytest

from . import validate

valid_id = '01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b'
invalid_id = 'z1ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b'


def test_machine_id():
    assert validate.machine_id(valid_id) is True
    with pytest.raises(TypeError):
        validate.machine_id(1337)
    with pytest.raises(ValueError):
        validate.machine_id(valid_id + 'b')
    with pytest.raises(ValueError):
        validate.machine_id(invalid_id)


def test_days():
    with pytest.raises(ValueError):
        validate.days(0)

    assert validate.days(1) is True
    assert validate.days(28) is True
    assert validate.days(0, zero_allowed=True) is True
    assert validate.days(1, zero_allowed=True) is True
    assert validate.days(28, zero_allowed=True) is True

    with pytest.raises(ValueError):
        validate.days(29)
    with pytest.raises(ValueError):
        validate.days(29, zero_allowed=True)
    with pytest.raises(ValueError):
        validate.days(-1)
    with pytest.raises(ValueError):
        validate.days(-1, zero_allowed=True)

    with pytest.raises(TypeError):
        validate.days('one')


def test_memory():
    assert validate.memory(1) is True
    assert validate.memory(2) is True
    with pytest.raises(TypeError):
        validate.memory(-1)
    with pytest.raises(ValueError):
        validate.memory(0)


def test_disk():
    assert validate.disk(10) is True
    with pytest.raises(ValueError):
        validate.disk(0)


def test_unsigned_int():
    assert validate.unsigned_int(0) is True
    assert validate.unsigned_int(1) is True
    assert validate.unsigned_int(1000) is True
    assert validate.unsigned_int(-1) is False
    assert validate.unsigned_int(1.0) is False
    assert validate.unsigned_int('a') is False
    assert validate.unsigned_int(None) is False


def test_bandwidth():
    assert validate.bandwidth(-1) is True
    assert validate.bandwidth(1) is True
    assert validate.bandwidth(0) is True
    assert validate.bandwidth(10) is True
    assert validate.bandwidth(1000000) is True
    with pytest.raises(ValueError):
        validate.bandwidth(-2)
    with pytest.raises(TypeError):
        validate.bandwidth(1.0)


def test_further_ipv4_ipv6():
    assert validate.further_ipv4_ipv6('tor', 'tor') is True
    assert validate.further_ipv4_ipv6('tor', False) is True
    assert validate.further_ipv4_ipv6(False, 'tor') is True
    with pytest.raises(ValueError):
        validate.further_ipv4_ipv6('tor', 1)
    with pytest.raises(ValueError):
        validate.further_ipv4_ipv6('nat', 'tor')


def test_organization():
    assert validate.organization(None) is True
    assert validate.organization('Corporation') is True
    assert validate.organization('google') is True
    assert validate.organization('Yahoo') is True
    # Shortest valid.
    assert validate.organization('A') is True
    # Longest valid
    valid = validate.organization(string.ascii_lowercase[:16])
    assert valid is True
    with pytest.raises(TypeError):
        validate.organization(False)
    with pytest.raises(TypeError):
        validate.organization(1234)
    # Too long
    with pytest.raises(ValueError):
        validate.organization(string.ascii_lowercase[:17])
    # Too short
    with pytest.raises(ValueError):
        validate.organization('')
    # Bad character
    with pytest.raises(ValueError):
        validate.organization('Google5')


def test_operating_system():
    assert validate.operating_system('debian-9') is True
    assert validate.operating_system('ubuntu-16-04') is True
    assert validate.operating_system(None) is True
    with pytest.raises(ValueError):
        validate.operating_system('windows')
    with pytest.raises(TypeError):
        validate.operating_system(1)


valid_ssh_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLuFASoTgo5r/bBGcawcN'\
                '7B/NTyjmEi3cdgl8r3ldZXVXl6N/7vfF/O6ggkU1iJCHUgxOqGHzJMyJ3ZL'\
                '6osyhgMF0htWYH7LhS4lJkzayUpCizelvW6FS//00smjxPnvOicEQNuuP0i'\
                'XYZVZIzbubZn8fJi0ZoJ5LkTpqNdAx1M420cplFGlcMww/jk0gGvlQZnEV4'\
                'Qra0Wh88s3xzPeryAoi+CwVAkBqHfntgkAVMComCfah8D+7nCS4F+Wi70hp'\
                'wrUhKulm3r5sOsyU1fGduvyL8XBYH8+yHwe5H+5TK5kJ6gAmyjNQ8fw+6Wk'\
                'wcB/heHAAJSUysYyfatIqKeWsj'

valid_ssh_key_with_comment = valid_ssh_key + ' root@localhost'


def test_ssh_key():
    assert validate.ssh_key(valid_ssh_key) is True
    assert validate.ssh_key(valid_ssh_key_with_comment) is True
    assert validate.ssh_key(None) is True
    with pytest.raises(TypeError):
        validate.ssh_key(1)
    with pytest.raises(ValueError):
        validate.ssh_key('')
    with pytest.raises(ValueError):
        validate.ssh_key('ssh-rsa')


def test_ipxescript():
    assert validate.ipxescript(None) is True
    assert validate.ipxescript('#!ipxe') is True
    with pytest.raises(TypeError):
        validate.ipxescript(1)
    with pytest.raises(TypeError):
        validate.ipxescript(True)
    with pytest.raises(ValueError):
        validate.ipxescript('')


def test_region():
    assert validate.region(None) is True
    assert validate.region('#!ipxe') is True
    with pytest.raises(TypeError):
        validate.region(1)
    with pytest.raises(TypeError):
        validate.region(True)
    with pytest.raises(ValueError):
        validate.region('')
