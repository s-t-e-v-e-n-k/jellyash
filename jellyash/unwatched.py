from operator import attrgetter
from typing import Optional

from .cli import argparse_parser
from .client import authed_client
from .search import search_single_show


def pluralized_str(count: int, prefix: str = "un") -> str:
    return f"{count} {prefix}watched episode{'s' if count != 1 else ''}"


def unwatched() -> None:
    parser = argparse_parser()
    parser.add_argument("show", nargs="*")
    parser.add_argument("-s", "--season", type=int)
    args = parser.parse_args()
    client = authed_client()
    if args.season and not args.show:
        parser.error("Need to specify a show when specifiying a season")
    if not args.show:
        all_unwatched(client)
    else:
        specific_unwatched(client, " ".join(args.show), season=args.season)


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


def specific_unwatched(client, term: str, season: Optional[int]) -> None:
    try:
        show = search_single_show(client, term)
    except ValueError as e:
        print(str(e))
        return
    seasons = client.jellyfin.get_seasons(show.Id)
    name = f"{show.Name}"
    if season is not None:
        try:
            show = next(s for s in seasons if s.IndexNumber == season)
        except StopIteration:
            print(f"Can not find season {season} of {name}")
            return
        if season >= 1:
            name += f", Season {season}"
        else:
            name += ", Specials"
        total = show.ChildCount
    else:
        total = sum(s.ChildCount for s in seasons)
    unwatched = show.UserData.UnplayedItemCount
    print(f"{name}: {pluralized_str(total - unwatched, prefix='')}")
    print(f"{name}: {pluralized_str(unwatched)}")
