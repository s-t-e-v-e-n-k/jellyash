from decimal import Decimal

from .cli import argparse_parser
from .client import authed_client
from .search import search_single_show


def calculate_duration(client, show: str) -> str:
    try:
        show = search_single_show(client, show)
    except ValueError as e:
        return str(e)
    count = 0
    duration = 0
    for season in client.jellyfin.get_seasons(show.Id):
        count += season.ChildCount
        episodes = client.jellyfin.get_season(show.Id, season.Id)
        duration += sum([e.RunTimeTicks for e in episodes])
    average = (duration / count) / int(Decimal("6E+008"))
    return f"Average duration over {count} episodes: {average:.1f} minutes"


def average_duration() -> None:
    parser = argparse_parser()
    parser.add_argument("show", nargs="+")
    args = parser.parse_args()
    client = authed_client()
    print(calculate_duration(client, " ".join(args.show)))
