import argparse
import unittest
from collections import namedtuple
from unittest.mock import Mock, patch

import pytest

from jellyash.bundle import Item
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
        specific_unwatched(self.test_client, self.show, None)
        captured = self.capsys.readouterr()
        wstr = "watched episode\n"
        expected = f"{self.show}: 1 {wstr}{self.show}: 1 un{wstr}"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched_with_season(self):
        specific_unwatched(self.test_client, self.show, 1)
        captured = self.capsys.readouterr()
        name = f"{self.show}, Season 1"
        wstr = "watched episode\n"
        expected = f"{name}: 1 {wstr}{name}: 1 un{wstr}"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched_unknown_season(self):
        specific_unwatched(self.test_client, self.show, 3)
        captured = self.capsys.readouterr()
        expected = "Can not find season 3 of Pioneer One\n"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched_unknown_special_season(self):
        # Season of specials is 0
        specific_unwatched(self.test_client, self.show, 0)
        captured = self.capsys.readouterr()
        # Pioneer One does not have a special season, but that is the actual
        # test. Without the fix, it returns all seasons.
        expected = "Can not find season 0 of Pioneer One\n"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.block_network
    def test_specific_unwatched_special_season(self):
        # Pioneer One does not have a special season, so we need to mock it.
        client_type = namedtuple('client', ['jellyfin'])
        client = client_type(Mock())
        show_dict = {
            "Id": 4,
            "Name": "Foo Bar"
            }
        special_dict = {
            "IndexNumber": 0,
            "ChildCount": 1,
            "UserData": {"UnplayedItemCount": 0}
            }
        client.jellyfin.get_seasons.return_value = [Item(special_dict)]
        with patch(
            "jellyash.unwatched.search_single_show",
            return_value=Item(show_dict)
            ):
            specific_unwatched(client, "Foo Bar", 0)
        captured = self.capsys.readouterr()
        name = "Foo Bar, Specials"
        wstr = "watched episode"
        expected = f"{name}: 1 {wstr}\n{name}: 0 un{wstr}s\n"
        self.assertEqual(captured.out, expected)
        self.assertEqual(captured.err, "")

    @pytest.mark.vcr
    def test_specific_unwatched_not_found(self):
        specific_unwatched(self.test_client, "NotFound", None)
        captured = self.capsys.readouterr()
        self.assertEqual(captured.out, "NotFound not found\n")
        self.assertEqual(captured.err, "")

    @pytest.mark.block_network
    def test_unwatched_season_without_show(self):
        with patch("jellyash.unwatched.authed_client"):
            with patch("argparse.ArgumentParser.parse_args",
                return_value=argparse.Namespace(show=[], season=3)
            ):
                # Sigh, parser.error will always exit.
                with self.assertRaises(SystemExit):
                    unwatched()
        captured = self.capsys.readouterr()
        self.assertEqual(captured.out, "")
        self.assertIn(
            "Need to specify a show when specifiying a season",
            captured.err
        )


class TestUnwatchedIntegration(unittest.TestCase):
    @pytest.mark.block_network
    def test_unwatched_all(self):
        with patch("jellyash.unwatched.authed_client") as client_mock:
            with patch("jellyash.unwatched.all_unwatched") as all_mock:
                with patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=argparse.Namespace(show=[], season=None)
                ):
                    unwatched()
                    all_mock.assert_called_once_with(client_mock())

    @pytest.mark.block_network
    def test_unwatched_specific(self):
        namespace = argparse.Namespace(show=["Foo", "Bar"], season=None)
        with patch("jellyash.unwatched.authed_client") as client_mock:
            with patch(
                "jellyash.unwatched.specific_unwatched") as specific_mock:
                with patch(
                    "argparse.ArgumentParser.parse_args",
                    return_value=namespace
                ):
                    unwatched()
                    specific_mock.assert_called_once_with(
                        client_mock(), "Foo Bar", season=None
                    )
