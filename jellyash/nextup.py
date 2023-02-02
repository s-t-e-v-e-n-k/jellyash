from .client import authed_client


def episode_str(episode):
    seasonindex = f"{episode.ParentIndexNumber}x{episode.IndexNumber:02}"
    return f"{episode.SeriesName} [{seasonindex}] {episode.Name}"


def nextup():
    client = authed_client()
    for episode in client.jellyfin.get_next(limit=30):
        print(episode_str(episode))

