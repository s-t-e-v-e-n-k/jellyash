from .bundle import Item
from .cli import argparse_parser
from .client import authed_client


def episode_str(episode: Item) -> str:
    seasonindex = f"{episode.ParentIndexNumber}x{episode.IndexNumber:0>2}"
    return f"{episode.SeriesName} [{seasonindex}] {episode.Name}"


def nextup() -> None:
    parser = argparse_parser()
    parser.add_argument("-l", "--limit", dest="limit", type=int, default=30)
    args = parser.parse_args()
    client = authed_client()
    for episode in client.jellyfin.get_next(limit=args.limit):
        print(episode_str(episode))
