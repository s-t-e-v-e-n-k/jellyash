from collections import defaultdict
from difflib import SequenceMatcher

from .bundle import Item


def search_single_show(client, term: str) -> Item:
    r = client.jellyfin.search_media_items(term=term, media="Series")
    if len(r) == 0:
        raise ValueError(f"{term} not found")
    else:
        matches = defaultdict(list)
        seq = SequenceMatcher(b=term)
        for series in r:
            seq.set_seq1(series.Name)
            matches[seq.ratio()].append(series)
        return matches[max(matches)][0]
