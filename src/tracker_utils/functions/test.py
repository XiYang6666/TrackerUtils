import asyncio
import ipaddress
import json
from pathlib import Path
from typing import Optional, TypedDict
from urllib.parse import urlparse

import aiodns
import httpx

from .. import config
from ..util import create_progress, create_rate_str, fail, if_sort, print, read_lines, retry_factory, write_lines

__all__ = ["test"]


async def download_trackers_list(tracker_provider_urls: list[str]):
    class GetTrackerListResult(TypedDict):
        url: str
        trackers: list[str]

    progress = create_progress()
    bar = progress.add_task("Downloading tracker lists", total=len(tracker_provider_urls))

    @retry_factory(progress, bar)
    async def get_tracker_list(client: httpx.AsyncClient, url: str) -> Optional[GetTrackerListResult]:
        try:
            response = await client.get(url)
            response.raise_for_status()
            tracker_list = read_lines(response.text)
            print(f"Downloaded {len(tracker_list)} tracker urls from “{url}”.")
            return {"url": url, "trackers": tracker_list}
        except Exception as e:
            fail(f"Failed to download “{url}”: {e}.")
            return None

    async with httpx.AsyncClient(timeout=config.timeout) as client:
        progress.start()
        tasks = [get_tracker_list(client, url) for url in tracker_provider_urls]
        results = await asyncio.gather(*tasks)
        progress.stop()
        all_trackers: set[str] = set()
        provider_map: dict[str, list[str]] = {}
        for result in results:
            if result is None:
                continue
            url = result["url"]
            trackers = result["trackers"]
            all_trackers.update(trackers)
            provider_map[url] = trackers
        return all_trackers, provider_map


def separate_trackers_by_protocol(trackers: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for tracker in trackers:
        parsed = urlparse(tracker)
        protocol = parsed.scheme
        if protocol in ["http", "https"]:
            protocol = "http(s)"
        if protocol not in result:
            result[protocol] = []
        result[protocol].append(tracker)
    return result


async def test_http_trackers(trackers: list[str]):
    progress = create_progress()
    bar = progress.add_task("Testing http(s) trackers", total=len(trackers))

    @retry_factory(progress, bar)
    async def try_connect_http_tracker(url: str) -> Optional[str]:
        try:
            await client.get(url)
            return url
        except Exception as e:
            fail(f"Failed to connect to “{url}”: {e}.")
            return None

    async with httpx.AsyncClient(
        timeout=config.timeout,
        limits=httpx.Limits(max_connections=100),
    ) as client:
        progress.start()

        tasks = [try_connect_http_tracker(url) for url in trackers]
        results = await asyncio.gather(*tasks)
        progress.stop()
        return [url for url in results if url is not None]


async def test_udp_trackers(trackers: list[str]):
    progress = create_progress()
    bar = progress.add_task("Testing udp trackers", total=len(trackers))

    @retry_factory(progress, bar)
    async def try_resolve_udp_tracker(url: str):
        parsed = urlparse(url)
        if parsed.scheme != "udp" or not parsed.hostname:
            print(f"Invalid UDP tracker URL: {url}.")
            return None

        # 检查是否为 IP 地址
        try:
            ipaddress.ip_address(parsed.hostname)
            return url
        except ValueError:
            pass

        # 解析域名
        fqdn = parsed.hostname
        try:
            a, aaaa = await asyncio.wait_for(
                asyncio.gather(
                    resolver.query(fqdn, "A"),
                    resolver.query(fqdn, "AAAA"),
                    return_exceptions=True,
                ),
                timeout=config.timeout,
            )

            if not isinstance(a, aiodns.error.DNSError) or not isinstance(aaaa, aiodns.error.DNSError):
                return url
            fail(f"Failed to resolve “{url}”({fqdn}): {a} & {aaaa}.")
            return None
        except Exception as e:
            fail(f"Failed to resolve “{url}”({fqdn}): {e}.")
            return None

    resolver = aiodns.DNSResolver(timeout=config.timeout)
    progress.start()
    tasks = [try_resolve_udp_tracker(url) for url in trackers]
    result = await asyncio.gather(*tasks)
    progress.stop()
    return [url for url in result if url is not None]


async def test(
    tracker_provider_urls: list[str],
    *,
    output_txt_dir: Optional[Path] = None,
    output_json_path: Optional[Path] = None,
    format_json: bool = False,
    sort: bool = True,
):
    # 下载tracker列表
    print("Downloading trackers from provider urls...")
    all_trackers, provider_map = await download_trackers_list(tracker_provider_urls)
    print(
        f"Download finished. {create_rate_str(len(provider_map), len(tracker_provider_urls))} provider available, "
        f"Total {len(all_trackers)} trackers found."
    )

    # 按协议分类
    print("Separating trackers by protocol...")
    separated_trackers = separate_trackers_by_protocol(list(all_trackers))
    protocol_types = list(separated_trackers.keys())
    protocol_types.sort()
    print("Separate finished. " + ", ".join([f"{protocol or 'unknown'}: {len(separated_trackers[protocol])}" for protocol in protocol_types]) + ".")

    # 测试tracker
    http_trackers = separated_trackers.get("http(s)", [])
    udp_trackers = separated_trackers.get("udp", [])
    print("Testing http(s) trackers...")
    available_http_trackers = await test_http_trackers(http_trackers)
    print(f"Finished. {create_rate_str(len(available_http_trackers), len(http_trackers))} http(s) trackers available.")
    print("Testing udp trackers...")
    available_udp_trackers = await test_udp_trackers(udp_trackers)
    print(f"Finished. {create_rate_str(len(available_udp_trackers), len(udp_trackers))} udp trackers available.")
    available_trackers = available_http_trackers + available_udp_trackers
    print(f"Test finished. {create_rate_str(len(available_trackers), len(all_trackers))} trackers available.")
    for provider, trackers in provider_map.items():
        available_counts = len([t for t in trackers if t in available_trackers])
        print(f"Availability of “{provider}”: {create_rate_str(available_counts, len(trackers))}.")

    # 输出结果
    # txt
    if output_txt_dir is not None:
        print(f"Saving output txt files to “{output_txt_dir}”...")
        # all
        write_lines(output_txt_dir / "all.txt", all_trackers, sort=sort)
        for protocol, trackers in separated_trackers.items():
            write_lines(output_txt_dir / f"all_{protocol}.txt", trackers)
        # available
        write_lines(output_txt_dir / "available.txt", available_trackers, sort=sort)
        for protocol, trackers in separated_trackers.items():
            write_lines(output_txt_dir / f"available_{protocol}.txt", [t for t in trackers if t in available_trackers], sort=sort)
        # extra data
    if output_json_path is not None:
        print(f"Saving output json file to “{output_json_path}”...")
        f = output_json_path.open("w")
        data = {
            "all": {
                "all": if_sort(all_trackers, sort),
                "available": if_sort(available_trackers, sort),
            },
            "protocol": {
                protocol: {
                    "all": if_sort(trackers, sort),
                    "available": if_sort([t for t in trackers if t in available_trackers], sort),
                }
                for protocol, trackers in separated_trackers.items()
            },
            "provider": {
                provider: {
                    "all": if_sort(trackers, sort),
                    "available": if_sort([t for t in trackers if t in available_trackers], sort),
                }
                for provider, trackers in provider_map.items()
            },
        }
        json.dump(data, f, indent=4 if format_json else None, ensure_ascii=False)
        f.close()
    print("Output files saved.")
