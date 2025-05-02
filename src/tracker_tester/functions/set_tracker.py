from dataclasses import dataclass
from typing import Optional

from qbittorrentapi import Client

from ..util import create_progress


@dataclass
class BtClientOptions:
    url: str
    user: Optional[str] = None
    pwd: Optional[str] = None


def set_tracker(
    tracker_urls: list[str],
    client_options: BtClientOptions,
):
    # 连接qbittorrent客户端
    print(f"Connecting to qBittorrent web api (url: {client_options.url}, user: {client_options.user})...")
    client = Client(host=client_options.url, username=client_options.user, password=client_options.pwd)
    print("Setting trackers...")
    all_torrents = client.torrents.info.all()
    progress = create_progress()
    progress.start()
    bar = progress.add_task("Setting trackers", total=len(all_torrents))
    for torrent in client.torrents.info.all():
        client.torrents_remove_trackers(torrent.hash, [t.url for t in torrent.trackers])
        client.torrents_add_trackers(torrent.hash, tracker_urls)
        progress.update(bar, advance=1)
    progress.stop()
    print("Done.")
