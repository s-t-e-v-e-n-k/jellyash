import unittest

import pytest

from jellyash.bundle import ApiResponse, Item

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
    def test_getitem_slice_start_end_no_jump(self):
        items = self.search_result[1:3]
        self.assertEqual(len(items), 2)
        self.assertEqual(
            items[0].Name, "18 - The Passenger of the 'Atlanta'")
        self.assertEqual(items[1].Name, "14 - Pickaxe and Trowel")

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_getitem_slice_start_end_with_jump(self):
        items = self.search_result[1:4:2]
        self.assertEqual(len(items), 2)
        self.assertEqual(
            items[0].Name, "18 - The Passenger of the 'Atlanta'")
        self.assertEqual(
            items[1].Name, "31 - Part II, Chapter 26: Bow and Arrow")

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_getitem_slice_only_end(self):
        items = self.search_result[:2]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].Name, "Blender Foundation")
        self.assertEqual(
            items[1].Name, "18 - The Passenger of the 'Atlanta'")

    @pytest.mark.default_cassette("TestApiResponse.setUp.yaml")
    @pytest.mark.vcr
    def test_getitem_slice_only_start(self):
        items = self.search_result[3:]
        self.assertEqual(len(items), 2)
        self.assertEqual(
            items[0].Name, "31 - Part II, Chapter 26: Bow and Arrow")
        self.assertEqual(
            items[1].Name, "22 - The New Citizen of the United States")

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


class TestUnwrappedApiResponse(ClientTest):
    @pytest.mark.vcr
    def test_unwrapped_dict_response(self):
        resp = self.test_client.jellyfin.try_server()
        self.assertFalse(isinstance(resp, ApiResponse))
        self.assertEqual(resp["ServerName"], "Stable Demo")

    @pytest.mark.vcr
    def test_unwrapped_bool_response(self):
        resp = self.test_client.jellyfin._get("QuickConnect/Enabled")
        self.assertFalse(resp)

