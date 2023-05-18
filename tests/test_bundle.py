import unittest

import pytest

from jellyash.bundle import Item
from .conftest import ClientTest


class TestItem(unittest.TestCase):
    def test_item(self):
        item = {"User": "demo"}
        wrapped = Item(item)
        self.assertDictEqual(wrapped._raw_item(), item)
        self.assertEqual(wrapped.User, "demo")
        with self.assertRaises(AttributeError):
            wrapped.user

    def test_nested_item(self):
        item = {"SessionInfo": {"UserName": "demo", "DeviceName": "bar"}}
        wrapped = Item(item)
        self.assertEqual(wrapped.SessionInfo.UserName, "demo")
        self.assertEqual(wrapped.SessionInfo.DeviceName, "bar")


class TestApiResponse(ClientTest):
    def setUp(self):
        self.search_result = self.test_client.jellyfin.search_media_items(
            term="", media="Movies", limit=5
        )

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_attrs(self):
        str_rep = "<ApiResponse object containing 95 items>"
        self.assertEqual(str(self.search_result), str_rep)
        self.assertEqual(len(self.search_result), 95)
        self.assertCountEqual(
            self.search_result._raw_value().keys(),
            ["Items", "TotalRecordCount", "StartIndex"]
        )

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_getitem(self):
        item = self.search_result[4]
        self.assertEqual(item.IndexNumber, 22)
        self.assertEqual(item.Type, "AudioBook")
        self.assertFalse(item.UserData.Played)
        self.assertEqual(item.UserData.PlayCount, 0)

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_iter(self):
        names = [
            "Blender Foundation",
            "18 - The Passenger of the 'Atlanta'",
            "14 - Pickaxe and Trowel",
            "31 - Part II, Chapter 26: Bow and Arrow",
            "22 - The New Citizen of the United States"
        ]
        self.assertSequenceEqual([m.Name for m in self.search_result], names)

