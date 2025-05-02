import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from qbittorrentapi import Client, Tracker  # 你妈的类型能不能好好写?
from rich import print

from .. import config
from ..util import create_progress, create_rate_str, fail, write_lines

__all__ = ["ClientTestOptions", "client_test"]


def get_torrent(client: Client, torrent: str):
    torrents = client.torrents.info.all()
    for t in torrents:
        if torrent == t.name or torrent == t.hash:
            return t
    return None


@dataclass
class ClientTestOptions:
    url: str
    torrent: str
    user: Optional[str] = None
    pwd: Optional[str] = None


async def client_test(
    trackers: list[str],
    client_options: ClientTestOptions,
    output_path: Path,
    *,
    fast_mode: bool = True,
    polling_interval: float = 3.0,
    yes_all: bool = False,
):
    trackers_set = set(trackers)
    # 连接qbittorrent客户端
    print(f"Connecting to qBittorrent web api (url: {client_options.url}, user: {client_options.user})...")
    client = Client(host=client_options.url, username=client_options.user, password=client_options.pwd)

    # 寻找测试种子
    test_torrent = get_torrent(client, client_options.torrent)
    if test_torrent is None:
        print(f"Torrent {client_options.torrent} not found in {client_options.url}.")
        return
    print(f"Found test torrent: {test_torrent.name}({test_torrent.hash})")

    # 清除原有的所有 tracker
    old_trackers = [t.url for t in test_torrent.trackers]

    # 从这里开始要考虑恢复原有tracker了
    try:
        client.torrents_remove_trackers(
            test_torrent.info.hash,
            urls=[t.url for t in test_torrent.trackers],
        )
        print(f"Removed all trackers from {test_torrent.name}.")

        # 添加新的测试tracker
        client.torrents_add_trackers(
            test_torrent.hash,
            urls=trackers_set,
        )
        print(f"Added {len(trackers_set)} trackers to “{test_torrent.name}”.")

        # 等待tracker生效
        contracted_trackers = set()
        available_trackers = set()

        progress = create_progress()
        progress.start()
        bar = progress.add_task("Waiting for all trackers to be contacted...", total=len(trackers_set))

        def check_has_data(t: Tracker):
            return t.num_downloaded != -1 or t.num_leeches != -1 or t.num_peers != -1 or t.num_seeds != -1

        async def wait_trackers():
            while True:
                await asyncio.sleep(polling_interval)
                torrent = get_torrent(client, client_options.torrent)
                if not torrent:
                    fail(f"Torrent “{client_options.torrent}” not found.")
                    continue
                for t in torrent.trackers:
                    if t.url not in trackers_set:
                        continue
                    elif t.status == 2:
                        contracted_trackers.add(t.url)
                        available_trackers.add(t.url)
                    elif t.status == 3 and check_has_data(t):
                        contracted_trackers.add(t.url)
                        available_trackers.add(t.url)
                    elif t.status == 3 and t.msg != "" and fast_mode:
                        if t.url not in contracted_trackers:
                            fail(f"Tracker “{t.url}” is not contactable(updating but failed): “{t.msg}”")
                        contracted_trackers.add(t.url)
                    elif t.status == 4:
                        if t.url not in contracted_trackers:
                            fail(f"Tracker “{t.url}” is not contactable(not working): “{t.msg}”")
                        contracted_trackers.add(t.url)

                progress.update(bar, completed=len(contracted_trackers))
                if contracted_trackers == trackers_set:
                    print("All trackers are contacted.")
                    break

        await asyncio.wait_for(wait_trackers(), timeout=config.timeout)
        progress.stop()
        print(f"Finished. {create_rate_str(len(available_trackers), len(trackers_set))} trackers are available.")
        if not yes_all:
            input("Press enter to continue.")
    except asyncio.TimeoutError:
        progress.stop()
        print("Timeouted while waiting for trackers to be contacted.")
        print(f"Finished. {create_rate_str(len(available_trackers), len(trackers_set))} trackers are available.")
        if not yes_all:
            input("Press enter to continue.")
    except Exception as e:
        progress.stop()
        raise e
    finally:
        # 恢复原有tracker
        test_torrent = get_torrent(client, client_options.torrent)
        if not test_torrent:
            fail(f"Torrent “{client_options.torrent}” not found.")
            return
        client.torrents_remove_trackers(
            test_torrent.hash,
            urls=[t.url for t in test_torrent.trackers],
        )
        print(f"Removed all testing trackers from “{test_torrent.name}”.")
        client.torrents_add_trackers(
            test_torrent.hash,
            urls=old_trackers,
        )
        print(f"Restored all original trackers to “{test_torrent.name}”.")
    # 保存结果
    print(f"Saving output file to “{output_path}”...")
    write_lines(output_path, available_trackers)
    print("Output files saved.")
