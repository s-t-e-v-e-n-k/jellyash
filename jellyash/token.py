import argparse
import json
from getpass import getpass as getpassword, getuser

from .client import create_client, auth_with_password, CREDENTIALS_FILE


def create_jellyfin_token():
    client = create_client('create_jellyfin_token')
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', dest='user', default=getuser())
    parser.add_argument(
        'server', nargs='?', default="https://jellyfin.wedontsleep.org/")
    args = parser.parse_args()
    password = getpassword()
    result = auth_with_password(client, args.server, args.user, password)
    if "AccessToken" in result:
        credentials = client.auth.credentials.get_credentials()
        server = credentials["Servers"][0]
        server["username"] = args.user
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(server, f)
        print("Credentials saved.")

