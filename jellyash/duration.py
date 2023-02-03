import argparse
from decimal import Decimal

from .client import authed_client
from .series import search_single_show


def average_duration():
    parser = argparse.ArgumentParser()
    parser.add_argument('show', nargs='+')
    args = parser.parse_args()
    client = authed_client()
    try:
        show = search_single_show(client, " ".join(args.show))
    except ValueError as e:
        print(str(e))
        return
    count = 0
    duration = 0
    for season in client.jellyfin.get_seasons(show.Id):
        count += season.ChildCount
        episodes = client.jellyfin.get_season(show.Id, season.Id)
        duration += sum([e.RunTimeTicks for e in episodes])
    average = (duration / count) / int(Decimal('6E+008'))
    print(f"Average duration over {count} episodes: {average:.1f} minutes")

