from operator import attrgetter
import sys

from .client import authed_client
from .series import search_single_show


def unwatched():
    client = authed_client()
    if len(sys.argv) == 1:
        all_unwatched(client)
    else:
        specific_unwatched(client)


def all_unwatched(client):
    r = client.jellyfin.search_media_items(term="", media="Series", limit=300)
    total = 0
    for series in sorted(r, key=attrgetter("Name")):
        if (count := series.UserData.UnplayedItemCount) > 0:
            ending = "s" if count != 1 else ''
            print(f"{series.Name}: {count} unwatched episode{ending}")
            total += count
    print(f"Total: {total} unwatched episodes")


def specific_unwatched(client):
    term = " ".join(sys.argv[1:])
    try:
        show = search_single_show(client, term)
    except ValueError as e:
        print(str(e))
        return
    unwatched = show.UserData.UnplayedItemCount
    total = sum(s.ChildCount for s in client.jellyfin.get_seasons(show.Id))
    print(f"{show.Name}: {total - unwatched} watched episodes")
    print(f"{show.Name}: {unwatched} unwatched episodes")

