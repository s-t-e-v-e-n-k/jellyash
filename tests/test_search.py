import json
import unittest
from collections import namedtuple
from unittest.mock import Mock

from jellyash.bundle import ApiResponse
from jellyash.client import authed_client
from jellyash.search import search_single_show


class TestSearch(unittest.TestCase):
    def setUp(self):
        with open(self.cassette_name(self.id().split(".")[-1])) as f:
            result = json.load(f)
        client_type = namedtuple('client', ['jellyfin'])
        self.client = client_type(Mock())
        self.client.jellyfin.search_media_items.return_value = ApiResponse(
            result
            )

    def test_term_not_found(self):
        with self.assertRaises(ValueError):
            search_single_show(self.client, "NotFound")

    def test_single_term(self):
        result = search_single_show(self.client, "Chernobyl")
        self.assertEqual(result.Name, "Chernobyl")

    def test_multiple_terms_not_exact(self):
        result = search_single_show(self.client, "NCIS: ")
        self.assertEqual(result.Name, "NCIS: Hawai'i")

    def test_multiple_terms_exact(self):
        result = search_single_show(self.client, "Maid")
        self.assertEqual(result.Name, "Maid")

    def test_multiple_terms_exact_with_space(self):
        result = search_single_show(self.client, "The Blacklist")
        self.assertEqual(result.Name, "The Blacklist")

    def cassette_name(self, test):
        return f"tests/cassettes/test_search/TestSearch.{test}.yaml"

    def _rerecord_mock_results(self):
        client = authed_client()
        test_cassettes = {
            "test_term_not_found": "NotFound",
            "test_single_term": "Chernobyl",
            "test_multiple_terms_not_exact": "NCIS: ",
            "test_multiple_terms_exact": "Maid",
            "test_multiple_terms_exact_with_space": "The Blacklist",
            }
        for test in test_cassettes:
            result = client.jellyfin.search_media_items(
                term=test_cassettes[test], media="Series"
                )
            with open(self.cassette_name(test), "w") as f:
                json.dump(result._raw_value(), f)


if __name__ == "__main__":
    TestSearch()._rerecord_mock_results()

