import argparse
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import pytest

from jellyash.token import create_jellyfin_token


class TestCreateJellyfinToken(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @pytest.mark.vcr
    def test_create_token(self):
        server_url = "https://demo.jellyfin.org/stable"
        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=argparse.Namespace(server=server_url, user="demo")
        ):
            with tempfile.NamedTemporaryFile() as tmpfile:
                ptf = pathlib.Path(tmpfile.name)
                with patch("jellyash.token.CREDENTIALS_FILE", ptf):
                    with patch(
                        "jellyash.token.getpassword", return_value=""
                    ):
                        create_jellyfin_token()
                captured = self.capsys.readouterr()
                self.assertEqual(captured.out, "Credentials saved.\n")
                self.assertEqual(captured.err, "")
                with open(ptf) as f:
                    credentials = json.load(f)
                self.assertEqual(credentials["address"], server_url)
                self.assertIn("AccessToken", credentials)
                self.assertIn("UserId", credentials)
                self.assertEqual(credentials["Name"], "Stable Demo")

