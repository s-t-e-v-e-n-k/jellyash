import unittest
from pathlib import Path

import pytest
import vcr

from jellyash.client import auth_with_password, create_client


def test_client(klass):
    dir_name = klass.__module__.split(".")[1]
    cassette_filename = f"{klass.__name__}.client.yaml"
    cassette = Path(f"tests/cassettes/{dir_name}/{cassette_filename}")
    if klass.is_recording:
        # vcrpy will not overwrite an existing cassette, remove it.
        cassette.unlink(missing_ok=True)
    with vcr.use_cassette(cassette, record_mode="once"):
        client = create_client()
        server_url = "https://demo.jellyfin.org/stable"
        auth_result = auth_with_password(client, server_url, "demo", "")
        assert "AccessToken" in auth_result
        return client


@pytest.fixture(scope="class")
def is_recording(request):
    is_recording = request.config.getoption("--record-mode") is not None
    request.cls.is_recording = is_recording


@pytest.mark.usefixtures("is_recording")
class ClientTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _client(self):
        self.test_client = test_client(self.__class__)

