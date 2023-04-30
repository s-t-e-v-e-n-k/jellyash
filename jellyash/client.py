import inspect
import json
import pathlib
import platform
import sys
from typing import Optional
from uuid import uuid4

from jellyfin_apiclient_python.client import JellyfinClient

from . import __version__
from .bundle import WrappedAPI

CREDENTIALS_FILE = pathlib.Path.home() / ".jellyfin_creds"


def create_client(app_name: Optional[str] = None):
    client = JellyfinClient()
    if not app_name:
        app_name = determine_app_name()
    client.config.app(app_name, __version__, platform.node(), str(uuid4()))
    client.config.data["auth.ssl"] = True
    client.jellyfin = WrappedAPI(client.http)
    return client


def auth_with_password(client, address: str, user: str, password: str):
    client.auth.connect_to_address(address)
    return client.auth.login(address, user, password)


def auth_with_token(client) -> None:
    if not CREDENTIALS_FILE.is_file():
        raise ValueError(f"{sys.argv[0]}: Requires credential file.")
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)
    client.authenticate({"Servers": [credentials]}, discover=False)


def authed_client():
    client = create_client(None)
    try:
        auth_with_token(client)
    except (PermissionError, ValueError, json.decoder.JSONDecodeError) as e:
        print(e)
        sys.exit(1)
    return client


def determine_app_name() -> str:
    frame = inspect.stack()[-2]
    return f"jellyfin_{inspect.getmodulename(frame.filename)}"

