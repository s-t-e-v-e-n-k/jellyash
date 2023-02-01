import json
import getpass
from pathlib import Path
import sys

from .client import create_client, auth_with_password


def create_jellyfin_token():
    client = create_client('create_jellyfin_token')
    if len(sys.argv) == 2:
        address = sys.argv[1]
    else:
        address = "https://jellyfin.wedontsleep.org/"
    password = getpass.getpass()
    result = auth_with_password(client, address, getpass.getuser(), password)
    if "AccessToken" in result:
        credentials = client.auth.credentials.get_credentials()
        server = credentials["Servers"][0]
        server["username"] = getpass.getuser()
        with open(Path.home() / ".jellyfin_creds", 'w') as f:
            json.dump(server, f)
        print("Credentials saved.")

