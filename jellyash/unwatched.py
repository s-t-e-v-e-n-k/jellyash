from operator import attrgetter

from .cli import argparse_parser
from .client import authed_client
from .search import search_single_show


def pluralized_str(count: int, prefix: str = "un") -> str:
    return f"{count} {prefix}watched episode{'s' if count != 1 else ''}"


def unwatched() -> None:
    client = authed_client()
    parser = argparse_parser()
    parser.add_argument("show", nargs="*")
    args = parser.parse_args()
    if not args.show:
        all_unwatched(client)
    else:
        specific_unwatched(client, " ".join(args.show))


def all_unwatched(client) -> None:
    r = client.jellyfin.search_media_items(
        term="", media="Series", limit=300
    )
    total = 0
    for series in sorted(r, key=attrgetter("Name")):
        if (count := series.UserData.UnplayedItemCount) > 0:
            print(f"{series.Name}: {pluralized_str(count)}")
            total += count
    print(f"Total: {pluralized_str(total)}")


def specific_unwatched(client, term: str) -> None:
    try:
        show = search_single_show(client, term)
    except ValueError as e:
        print(str(e))
        return
    unwatched = show.UserData.UnplayedItemCount
    total = sum(s.ChildCount for s in client.jellyfin.get_seasons(show.Id))
    count = total - unwatched
    print(f"{show.Name}: {pluralized_str(count, prefix='')}")
    print(f"{show.Name}: {pluralized_str(unwatched)}")
