import json
import pathlib
import platform
import tempfile
import unittest
from unittest.mock import patch

import pytest

from jellyash import __version__
from jellyash.client import (
    auth_with_password, auth_with_token, create_client
    )


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = create_client("test")

    def test_create_client_with_app_name(self):
        data = self.client.config.data
        self.assertEqual(data['app.name'], "test")
        self.assertEqual(data['app.device_name'], platform.node())
        self.assertEqual(data['app.version'], __version__)
        self.assertTrue(data['auth.ssl'])
    
    @pytest.mark.vcr
    def test_auth_with_password(self):
        server_url = "https://demo.jellyfin.org/stable"
        auth_result = auth_with_password(self.client, server_url, "demo", "")
        self.assertEqual(auth_result["User"]["Name"], "demo")
        self.assertEqual(auth_result["SessionInfo"]["UserName"], "demo")
        self.assertEqual(
            auth_result["SessionInfo"]["DeviceName"],
            platform.node()
        )


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
            ptf = pathlib.Path(tmpfile.name)
            with patch("jellyash.client.CREDENTIALS_FILE", ptf):
                with self.assertRaises(json.decoder.JSONDecodeError):
                    auth_with_token(None)

    def test_auth_with_nonexistant_file(self):
        non_exist = pathlib.Path("/does/not/exist")
        with patch("jellyash.client.CREDENTIALS_FILE", non_exist):
            with self.assertRaises(ValueError):
                auth_with_token(None)
