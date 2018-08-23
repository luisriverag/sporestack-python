import pytest

from . import ssh


def test_ssh_bad_option_combination():
    with pytest.raises(ValueError):
        ssh.ssh('127.0.0.1',
                'foobar_command',
                stdin='data',
                interactive=True)
