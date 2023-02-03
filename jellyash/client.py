import json
import inspect
from pathlib import Path
import platform
from uuid import uuid4
import sys

from jellyfin_apiclient_python.api import API
from jellyfin_apiclient_python.client import JellyfinClient

from . import __version__


CREDENTIALS_FILE = Path.home() / ".jellyfin_creds"


class WrappedAPI(API):
    def _get(self, handler, params=None):
        return ApiResponse(super()._get(handler, params=params))


def create_client(app_name=None):
    client = JellyfinClient()
    if not app_name:
        app_name = determine_app_name()
    client.config.app(app_name, __version__, platform.node(), str(uuid4()))
    client.config.data["auth.ssl"] = True
    client.jellyfin = WrappedAPI(client.http)
    return client


def auth_with_password(client, address, user, password):
    client.auth.connect_to_address(address)
    return client.auth.login(address, user, password)


def auth_with_token(client):
    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.load(f)
    client.authenticate({"Servers": [credentials]}, discover=False)


def authed_client():
    if not CREDENTIALS_FILE.is_file():
        print(f"{sys.argv[0]}: Requires credential file.")
        sys.exit(1)
    client = create_client(None)
    auth_with_token(client)
    return client


def determine_app_name():
    frame = inspect.stack()[-2]
    return f"jellyfin_{inspect.getmodulename(frame.filename)}"


class ApiResponse:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"<ApiResponse object containing {len(self)} items>"

    def __iter__(self):
        yield from [Item(i) for i in self.value["Items"]]

    def __getitem__(self, key):
        return Item(self.value["Items"][key])

    def __len__(self):
        return self.value["TotalRecordCount"] + self.value["StartIndex"]


class Item:
    def __init__(self, item):
        self.item = item

    def _raw_item(self):
        return self.item

    def __getattr__(self, attr):
        try:
            value = self.item[attr]
            if isinstance(value, dict):
                value = Item(value)
            return value
        except KeyError:
            raise AttributeError(f"Item has no attribute '{attr}'")

