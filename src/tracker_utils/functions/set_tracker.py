from dataclasses import dataclass
from typing import Optional

from qbittorrentapi import Client

from ..utils.functions import load_all_tracker
from ..utils.output import create_progress, print


@dataclass
class BtClientOptions:
    url: str
    user: Optional[str] = None
    pwd: Optional[str] = None


async def set_tracker(
    tracker_urls: list[str],
    client_options: BtClientOptions,
    append: bool = False,
):
    all_trackers, _ = await load_all_tracker(tracker_urls)

    # 连接qbittorrent客户端
    print(f"Connecting to qBittorrent web api (url: {client_options.url}, user: {client_options.user})...")
    client = Client(host=client_options.url, username=client_options.user, password=client_options.pwd)
    print("Setting trackers...")
    all_torrents = client.torrents.info.all()
    progress = create_progress()
    progress.start()
    bar = progress.add_task("Setting trackers", total=len(all_torrents))
    for torrent in client.torrents.info.all():
        if not append:
            client.torrents_remove_trackers(torrent.hash, [t.url for t in torrent.trackers])
        client.torrents_add_trackers(torrent.hash, all_trackers)
        progress.update(bar, advance=1)
    progress.stop()
    print("Done.")
