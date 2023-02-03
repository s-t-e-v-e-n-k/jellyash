# Jellyash

Jelly **A**eroplane **S**hark **H**elper

Wrapper around jellyfin-apiclient-python to provide convenience functions:

Create an unauthenticated client:

```
create_client(app_name)
```

Authenticate with username and password:

```
auth_with_password(client, address, user, password)
```

Authenticate with a written out token:

```
auth_with_token(client)
```
This reads from `~/.jellyfin_creds` via JSON

## Provided scripts

* `create_jellyfin_token` writes out a token.
* `nextup` displays all episodes Next Up.
* `unwatched` displays all shows with unwatched episodes, and can query one show directly.
* `average_duration` displays the average episode length of a given show.
