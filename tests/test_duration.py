import argparse
from unittest.mock import patch

import pytest

from jellyash.duration import average_duration, calculate_duration

from .conftest import ClientTest


class TestDuration(ClientTest):
    @pytest.mark.vcr
    def test_calculate_duration_not_found(self):
        result = calculate_duration(self.test_client, "NotFound")
        self.assertEqual(result, "NotFound not found")

    @pytest.mark.vcr
    def test_calculate_duration(self):
        result = calculate_duration(self.test_client, "Pioneer One")
        expected = "Average duration over 2 episodes: 5.4 minutes"
        self.assertEqual(result, expected)

    @pytest.mark.block_network
    def test_integration(self):
        with patch("jellyash.duration.authed_client") as client_mock:
            with patch(
                "argparse.ArgumentParser.parse_args",
                return_value=argparse.Namespace(show=["Foo", "Bar"])
            ):
                with patch(
                    "jellyash.duration.calculate_duration") as avg_mock:
                    average_duration()
                    client_mock.assert_called_once()
                    avg_mock.assert_called_once_with(
                        client_mock(), "Foo Bar"
                    )

