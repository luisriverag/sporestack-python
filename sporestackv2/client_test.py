from . import client


def test_random_machine_id():
    assert len(client.random_machine_id()) == 64


def test_api_endpoint_to_host():
    assert client.api_endpoint_to_host("http://foo.bar") == "foo.bar"
    assert client.api_endpoint_to_host("https://foo.bar") == "foo.bar"


def test_version():
    assert "." in client.version()
