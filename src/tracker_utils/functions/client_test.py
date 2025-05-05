import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from qbittorrentapi import Client, Tracker  # 你妈的类型能不能好好写?
from qbittorrentapi.torrents import TorrentDictionary

from .. import config
from ..utils.base import write_lines
from ..utils.functions import load_all_tracker, show_test_result
from ..utils.output import create_progress, fail, print

__all__ = ["ClientTestOptions", "client_test"]


def get_torrent(client: Client, torrent_id: str):
    torrents = client.torrents.info.all()
    for t in torrents:
        if torrent_id == t.name or torrent_id == t.hash:
            return t
    raise ValueError(f"Torrent “{torrent_id}” not found.")


def remove_trackers(client: Client, torrent: TorrentDictionary, trackers: list[str]):
    client.torrents_remove_trackers(torrent.hash, urls=trackers)


def add_trackers(client: Client, torrent: TorrentDictionary, trackers: list[str]):
    client.torrents_add_trackers(torrent.hash, urls=trackers)


def get_tracker_infos(torrent: TorrentDictionary) -> list[Tracker]:
    return [t for t in torrent.trackers if not t.url.startswith("**")]


def get_tracker_urls(torrent: TorrentDictionary) -> list[str]:
    return [t.url for t in torrent.trackers if not t.url.startswith("**")]


@dataclass
class ClientTestOptions:
    url: str
    torrent: str
    user: Optional[str] = None
    pwd: Optional[str] = None


async def client_test(
    tracker_urls: list[str],
    client_options: ClientTestOptions,
    output_path: Path,
    *,
    polling_interval: float = 3.0,
    batch_size: int = 20,
    fast_mode: bool = True,
):
    all_trackers, provider_map = await load_all_tracker(tracker_urls)

    # 连接qbittorrent客户端
    print(f"Connecting to qBittorrent web api (url: {client_options.url}, user: {client_options.user})...")
    client = Client(host=client_options.url, username=client_options.user, password=client_options.pwd)

    # 寻找测试种子
    test_torrent = get_torrent(client, client_options.torrent)
    print(f"Found test torrent: “{test_torrent.name}”({test_torrent.hash})")

    # 保存原有 tracker
    old_trackers = get_tracker_urls(test_torrent)

    # 分批测试

    progress = create_progress()
    bar = progress.add_task("Waiting for all trackers to be contacted", total=len(all_trackers))

    tested_trackers_count = 0
    available_trackers = []

    def check_has_data(t: Tracker):
        return t.num_downloaded != -1 or t.num_leeches != -1 or t.num_peers != -1 or t.num_seeds != -1

    async def wait_trackers(trackers: list[str]):
        nonlocal tested_trackers_count
        contracted_trackers = []
        # 轮询tracker状态

        while True:
            await asyncio.sleep(polling_interval)
            torrent = get_torrent(client, client_options.torrent)
            for t in get_tracker_infos(torrent):
                if t.url not in trackers:
                    continue
                elif t.url in contracted_trackers:
                    continue
                elif t.status == 2:
                    contracted_trackers.append(t.url)
                    available_trackers.append(t.url)
                elif t.status == 3 and check_has_data(t):
                    contracted_trackers.append(t.url)
                    available_trackers.append(t.url)
                elif t.status == 3 and t.msg != "" and fast_mode:
                    if t.url not in contracted_trackers:
                        fail(f"Tracker “{t.url}” is not contactable(updating but failed): “{t.msg}”")
                    contracted_trackers.append(t.url)
                elif t.status == 4:
                    if t.url not in contracted_trackers:
                        fail(f"Tracker “{t.url}” is not contactable(not working): “{t.msg}”")
                    contracted_trackers.append(t.url)
            progress.update(bar, completed=tested_trackers_count + len(contracted_trackers))
            if len(contracted_trackers) == len(trackers):
                break

    async def test_tracker(trackers: list[str]):
        # 删除原有tracker
        torrent = get_torrent(client, client_options.torrent)  # type: ignore
        remove_trackers(client, torrent, get_tracker_urls(torrent))
        print(f"Removed all trackers from “{test_torrent.name}”.")

        # 添加新的测试tracker
        add_trackers(client, test_torrent, trackers)
        print(f"Added {len(trackers)} trackers to “{test_torrent.name}”.")
        # 等待tracker可用
        await wait_trackers(trackers)

    # 开始测试
    # (从这里开始要考虑失败后恢复原有tracker了)
    try:
        progress.start()
        batch_count = len(all_trackers) // batch_size
        if len(all_trackers) % batch_size != 0:
            batch_count += 1
        for i in range(0, len(all_trackers), batch_size):
            batch_id = i // batch_size + 1
            batch_trackers = all_trackers[i : i + batch_size]
            print(f"Testing batch {batch_id}/{batch_count}...")
            try:
                await asyncio.wait_for(test_tracker(batch_trackers), timeout=config.timeout)
            except asyncio.TimeoutError:
                fail("Timeout, skippping current batch.")
            finally:
                tested_trackers_count += len(batch_trackers)
                progress.update(bar, completed=tested_trackers_count)
    finally:
        progress.stop()
        # 恢复原有tracker
        test_torrent = get_torrent(client, client_options.torrent)  # type: ignore
        if not test_torrent:
            fail(f"Torrent “{client_options.torrent}” not found.")
            return
        remove_trackers(client, test_torrent, get_tracker_urls(test_torrent))
        print(f"Removed all testing trackers from “{test_torrent.name}”.")
        add_trackers(client, test_torrent, old_trackers)
        print(f"Restored all original trackers to “{test_torrent.name}”.")
    show_test_result(all_trackers, available_trackers, provider_map)
    # 保存结果
    print(f"Saving output file to “{output_path}”...")
    write_lines(output_path, available_trackers)
    print("Output files saved.")
