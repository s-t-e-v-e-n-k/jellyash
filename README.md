Jellyash

Wrapper around jellyfin-apiclient-python to provide convience functions:

Create an unauthenticated client:
`create_client(app_name, app_version)`

Authenicate with username and password:
`auth_with_password(client, address, user, password)`

Authenicate with a written out token:
`auth_with_token(client)`
This reads from ~/.jellyfin_creds with JSON
