import asyncio
from typing import Optional, TypedDict

import httpx

from .. import config
from .base import create_rate_str, read_lines
from .decorators import retry_factory
from .output import create_progress, fail, print


async def download_trackers_list(tracker_provider_urls: set[str]):
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


async def load_all_tracker(urls: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    results = {u for u in urls if not u.startswith("[PROVIDER]")}
    provider_map = {"[OPTIONS]": list(results)}
    providers = {u.removeprefix("[PROVIDER]") for u in urls if u.startswith("[PROVIDER]")}
    if providers:
        print("Downloading trackers from provider urls...")
        trackers, map = await download_trackers_list(providers)
        print(f"Download finished. {create_rate_str(len(map), len(providers))} provider available, Total {len(trackers)} trackers found.")
        results.update(trackers)
        provider_map.update(map)

    return list(results), provider_map


def show_test_result(all_trackers: list[str], available_trackers: list[str], provider_map: dict[str, list[str]]):
    print(f"Test finished. {create_rate_str(len(available_trackers), len(all_trackers))} trackers available.")
    for provider, trackers in provider_map.items():
        available_counts = len([t for t in trackers if t in available_trackers])
        print(f"Availability of “{provider}”: {create_rate_str(available_counts, len(trackers))}.")
