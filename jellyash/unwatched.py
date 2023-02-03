import argparse
from operator import attrgetter

from .client import authed_client
from .series import search_single_show


def unwatched():
    client = authed_client()
    parser = argparse.ArgumentParser()
    parser.add_argument('show', nargs='*')
    args = parser.parse_args()
    if not args.show:
        all_unwatched(client)
    else:
        specific_unwatched(client, " ".join(args.show))


def all_unwatched(client):
    r = client.jellyfin.search_media_items(term="", media="Series", limit=300)
    total = 0
    for series in sorted(r, key=attrgetter("Name")):
        if (count := series.UserData.UnplayedItemCount) > 0:
            ending = "s" if count != 1 else ''
            print(f"{series.Name}: {count} unwatched episode{ending}")
            total += count
    print(f"Total: {total} unwatched episodes")


def specific_unwatched(client, term):
    try:
        show = search_single_show(client, term)
    except ValueError as e:
        print(str(e))
        return
    unwatched = show.UserData.UnplayedItemCount
    total = sum(s.ChildCount for s in client.jellyfin.get_seasons(show.Id))
    print(f"{show.Name}: {total - unwatched} watched episodes")
    print(f"{show.Name}: {unwatched} unwatched episodes")

