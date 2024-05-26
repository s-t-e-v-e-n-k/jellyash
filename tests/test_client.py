import json
import pathlib
import platform
import tempfile
import unittest
from unittest.mock import Mock, patch

import pytest
from jellyfin_apiclient_python.client import JellyfinClient

from jellyash import __version__
from jellyash.client import (
    auth_with_password,
    auth_with_token,
    authed_client,
    create_client,
)

from .conftest import ClientTest


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = create_client()

    def test_create_client(self):
        data = self.client.config.data
        self.assertEqual(data['app.name'], "jellyash")
        self.assertEqual(data['app.device_name'], platform.node())
        self.assertEqual(data['app.version'], __version__)
        self.assertTrue(data['auth.ssl'])

    @pytest.mark.vcr
    def test_auth_with_password(self):
        server_url = "https://demo.jellyfin.org/stable"
        auth_result = auth_with_password(self.client, server_url, "demo", "")
        self.assertEqual(auth_result["User"]["Name"], "demo")
        self.assertEqual(auth_result["SessionInfo"]["UserName"], "demo")
        self.assertEqual(auth_result["SessionInfo"]["DeviceName"], "wrecked")


class TestAuthWithToken(unittest.TestCase):
    def test_auth_with_token_credential_directory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            ptd = pathlib.Path(tempdir)
            with patch("jellyash.client.CREDENTIALS_FILE", ptd):
                with self.assertRaises(ValueError):
                    auth_with_token(None)

    def test_auth_with_token_unreadable_file(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            ptf = pathlib.Path(tmpfile.name)
            ptf.chmod(0o0000)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                with self.assertRaises(PermissionError):
                    auth_with_token(None)
            ptf.chmod(0o600)

    def test_auth_with_token_invalid_json(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.file.write(b"{{\n")
            tmpfile.file.flush()
            ptf = pathlib.Path(tmpfile.name)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                with self.assertRaises(json.decoder.JSONDecodeError):
                    auth_with_token(None)

    def test_auth_with_nonexistant_file(self):
        non_exist = pathlib.Path("/does/not/exist")
        with patch("jellyash.client.CREDENTIALS_FILE", non_exist):
            with self.assertRaises(ValueError):
                auth_with_token(None)

    def test_auth_with_state_zero(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.file.write(b"{\"User\": \"foo\"}\n")
            tmpfile.file.flush()
            ptf = pathlib.Path(tmpfile.name)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                client_mock = Mock()
                client_mock.authenticate.return_value = {"State": 0}
                with self.assertRaises(ConnectionError):
                    auth_with_token(client_mock)
                client_mock.authenticate.assert_called_once()


class TestAuthedClient(ClientTest):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @pytest.mark.vcr
    def test_authed_client(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            credentials = self.test_client.auth.credentials.get_credentials()
            with open(tmpfile.name, 'w') as f:
                json.dump(credentials["Servers"][0], f)
            ptf = pathlib.Path(tmpfile.name)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                client = authed_client()
                self.assertTrue(isinstance(client, JellyfinClient))

    @pytest.mark.vcr
    def test_authed_client_offline(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            credentials = self.test_client.auth.credentials.get_credentials()
            with open(tmpfile.name, 'w') as f:
                json.dump(credentials["Servers"][0], f)
            ptf = pathlib.Path(tmpfile.name)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                with patch("sys.argv", ["test_offline"]):
                    with self.assertRaises(SystemExit):
                        authed_client()
        captured = self.capsys.readouterr()
        self.assertEqual(
            captured.out, "test_offline: Failed to establish connection\n"
            )
        self.assertEqual(captured.err, "")

    def test_authed_client_non_existant_file(self):
        non_exist = pathlib.Path("/does/not/exist")
        with patch("jellyash.client.CREDENTIALS_FILE", non_exist):
            with self.assertRaises(SystemExit):
                authed_client()
