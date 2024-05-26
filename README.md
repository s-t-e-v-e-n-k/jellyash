# Jellyash

[![PyPI Version](https://badge.fury.io/py/jellyash.svg)](https://badge.fury.io/py/jellyash)[![Build](https://github.com/s-t-e-v-e-n-k/jellyash/actions/workflows/ci.yml/badge.svg)](https://github.com/s-t-e-v-e-n-k/jellyash/actions/workflows/ci.yml)[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/s-t-e-v-e-n-k/0926cbcb886804fa2c0fdb68212a367d/raw/coverage-badge.json)](https://gist.github.com/s-t-e-v-e-n-k/0926cbcb886804fa2c0fdb68212a367d/raw/coverage-badge.json)

Jelly **A**eroplane **S**hark **H**elper

Wrapper around jellyfin-apiclient-python to provide convenience functions:

Create an unauthenticated client:

```
create_client()
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
