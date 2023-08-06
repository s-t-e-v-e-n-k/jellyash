import argparse
import unittest
from collections import namedtuple
from unittest.mock import Mock, patch

import pytest

from jellyash.bundle import Item
from jellyash.nextup import episode_str, nextup

from .conftest import ClientTest


class TestEpisodeStr(ClientTest):
    @pytest.mark.vcr
    def test_episode_str(self):
        result = self.test_client.jellyfin.search_media_items(
            "The Man From Mars", media="Episodes"
        )
        episode = next((e for e in result if e.Type == "Episode"), None)
        self.assertIsNotNone(episode)
        self.assertEqual(
            episode_str(episode), "Pioneer One [1x02] The Man From Mars"
        )


class TestNextUp(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @pytest.mark.block_network
    def test_nextup(self):
        client_type = namedtuple('client', ['jellyfin'])
        client = client_type(Mock())
        episode_dict = {
            'Name': 'Bar',
            'ParentIndexNumber': '4',
            'IndexNumber': '20',
            'SeriesName': 'Foo',
            }
        client.jellyfin.get_next.return_value = [Item(episode_dict)]
        with patch("jellyash.nextup.authed_client", return_value=client):
            with patch(
                "argparse.ArgumentParser.parse_args",
                return_value=argparse.Namespace(limit=10)
            ):
                nextup()
                client.jellyfin.get_next.assert_called_once_with(limit=10)
                captured = self.capsys.readouterr()
                self.assertEqual(captured.out, "Foo [4x20] Bar\n")
                self.assertEqual(captured.err, "")

