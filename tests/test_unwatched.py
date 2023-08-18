import argparse
import unittest
from unittest.mock import patch

import pytest

from jellyash.unwatched import (
    all_unwatched,
    pluralized_str,
    specific_unwatched,
    unwatched,
)

from .conftest import ClientTest


class TestPluralizedStr(unittest.TestCase):
    def test_pluralized_str(self):
        self.assertEqual("0 unwatched episodes", pluralized_str(0))
        self.assertEqual("1 unwatched episode", pluralized_str(1))
        self.assertEqual("2 unwatched episodes", pluralized_str(2))
        self.assertEqual(
            "1 dewatched episode", pluralized_str(1, prefix="de")
        )


class TestUnwatched(ClientTest):
    def setUp(self):
        self.show = "Pioneer One"

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @pytest.mark.vcr
    def test_all_unwatched(self):
        all_unwatched(self.test_client)
        captured = self.capsys.readouterr()
        ustr = "unwatched episode\n"
        expected = f"{self.show}: 1 {ustr}Total: 1 {ustr}"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched(self):
        specific_unwatched(self.test_client, "Pioneer One")
        captured = self.capsys.readouterr()
        wstr = "watched episode\n"
        expected = f"{self.show}: 1 {wstr}{self.show}: 1 un{wstr}"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched_not_found(self):
        specific_unwatched(self.test_client, "NotFound")
        captured = self.capsys.readouterr()
        self.assertEqual(captured.out, "NotFound not found\n")
        self.assertEqual(captured.err, "")


class TestUnwatchedIntegration(unittest.TestCase):
    @pytest.mark.block_network
    def test_unwatched_all(self):
        with patch("jellyash.unwatched.authed_client") as client_mock:
            with patch("jellyash.unwatched.all_unwatched") as all_mock:
                with patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(show=[])
                ):
                    unwatched()
                    all_mock.assert_called_once_with(client_mock())

    @pytest.mark.block_network
    def test_unwatched_specific(self):
        with patch("jellyash.unwatched.authed_client") as client_mock:
            with patch(
                "jellyash.unwatched.specific_unwatched") as specific_mock:
                with patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(show=["Foo", "Bar"])
                ):
                    unwatched()
                    specific_mock.assert_called_once_with(
                        client_mock(), "Foo Bar"
                    )

