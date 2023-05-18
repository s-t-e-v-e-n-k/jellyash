import unittest

import pytest
import vcr

from jellyash.client import auth_with_password, create_client


def test_client(klass):
    dir_name = klass.__module__.split(".")[1]
    cassette_filename = f"{klass.__name__}.client.yaml"
    cassette = f"tests/cassettes/{dir_name}/{cassette_filename}"
    with vcr.use_cassette(cassette, record_mode="once"):
        client = create_client(f"jellyash_test_{klass.__name__.lower()}")
        server_url = "https://demo.jellyfin.org/stable"
        auth_result = auth_with_password(client, server_url, "demo", "")
        assert "AccessToken" in auth_result
        return client


class ClientTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _client(self):
        self.test_client = test_client(self.__class__)

