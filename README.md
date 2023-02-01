Jellyash

Wrapper around jellyfin-apiclient-python to provide convenience functions:

Create an unauthenticated client:
`create_client(app_name, app_version)`

Authenticate with username and password:
`auth_with_password(client, address, user, password)`

Authenticate with a written out token:
`auth_with_token(client)`
This reads from ~/.jellyfin_creds via JSON

`create_jellyfin_token` writes out a token.
