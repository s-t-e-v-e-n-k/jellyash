import unittest

from jellyash.bundle import ApiResponse, Item


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


class TestApiResponse(unittest.TestCase):
    def test_str(self):
        pass

