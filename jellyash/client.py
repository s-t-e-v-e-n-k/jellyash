import json
import pathlib
import platform
import sys
from json.decoder import JSONDecodeError
from uuid import uuid4

from jellyfin_apiclient_python.client import JellyfinClient
from jellyfin_apiclient_python.connection_manager import CONNECTION_STATE

from . import __version__
from .bundle import WrappedAPI

CREDENTIALS_FILE = pathlib.Path.home() / ".jellyfin_creds"


def create_client():
    client = JellyfinClient()
    client.config.app("jellyash", __version__, platform.node(), str(uuid4()))
    client.config.data["auth.ssl"] = True
    client.jellyfin = WrappedAPI(client.http)
    return client


def auth_with_password(client, address: str, user: str, password: str):
    client.auth.connect_to_address(address)
    return client.auth.login(address, user, password)


def auth_with_token(client) -> None:
    if not CREDENTIALS_FILE.is_file():
        raise ValueError(f"{sys.argv[0]}: Requires credential file.")
    with open(CREDENTIALS_FILE) as f:
        credentials = json.load(f)
    state = client.authenticate({"Servers": [credentials]}, discover=False)
    if state["State"] != CONNECTION_STATE["SignedIn"]:
        raise ConnectionError("Failed to establish connection")


def authed_client():
    client = create_client()
    try:
        auth_with_token(client)
    except (
        PermissionError, ValueError, JSONDecodeError, ConnectionError
        ) as e:
        print(f"{sys.argv[0]}: {e}")
        sys.exit(1)
    return client

