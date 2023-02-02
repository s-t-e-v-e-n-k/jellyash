from decimal import Decimal
import sys

from .client import authed_client
from .series import search_single_show


def average_duration():
    if len(sys.argv) == 1:
        print(f"{sys.argv[0]}: Need a show argument")
        return
    client = authed_client()
    term = " ".join(sys.argv[1:])
    try:
        show = search_single_show(client, term)
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

