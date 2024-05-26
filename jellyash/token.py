import json
from getpass import getpass as getpassword
from getpass import getuser

from .cli import argparse_parser
from .client import CREDENTIALS_FILE, auth_with_password, create_client


def create_jellyfin_token() -> None:
    parser = argparse_parser()
    parser.add_argument("-u", "--user", dest="user", default=getuser())
    parser.add_argument(
        "server", nargs="?", default="https://jellyfin.wedontsleep.org/"
    )
    args = parser.parse_args()
    password = getpassword()
    client = create_client()
    result = auth_with_password(client, args.server, args.user, password)
    if "AccessToken" in result:
        credentials = client.auth.credentials.get_credentials()
        server = credentials["Servers"][0]
        server["username"] = args.user
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(server, f)
        print("Credentials saved.")
