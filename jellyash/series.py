def search_single_show(client, term):
    r = client.jellyfin.search_media_items(term=term, media="Series")
    if len(r) == 0:
        raise ValueError(f"{term} not found")
    elif len(r) > 1:
        exact = not " " in term
        for idx, series in enumerate(r):
            if exact and term == series.Name:
                break
            elif not exact and term in series.Name:
                break
    else:
        idx = 0
    return r[idx]

