import asyncio
import logging
import pprint

import httpx

from miner.miner.custom_types import EventSchema
from miner.miner.helpers import flatten_2d_container
from miner.miner.sources.hackathon_rus_events import get_hackathon_rus_events
from miner.miner.sources.illusion_events import get_illusion_events
from miner.miner.sources.sber_events import get_sber_events
from miner.miner.sources.sk_events import get_sk_events
from miner.miner.sources.tinkoff_events import get_tinkoff_events
from miner.miner.sources.vk_cloud_events import get_vk_cloud_events
from miner.miner.sources.vk_events import get_vk_events
from miner.miner.sources.yandex_events import get_yandex_events

logger = logging.getLogger(__name__)


TASKS = [
    get_hackathon_rus_events,
    get_illusion_events,
    get_sber_events,
    get_tinkoff_events,
    get_yandex_events,
    get_vk_cloud_events,
    get_vk_events,
    get_sk_events,
]


async def mine_data(is_printing: bool = False) -> list[EventSchema]:
    results: list[list[EventSchema]] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [task(client) for task in TASKS]

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
            except Exception as error:
                logger.error("Error occurred while running a task!")
                logger.error(str(error))
            else:
                results.append(result)

    flattened_results = flatten_2d_container(results)

    if is_printing:
        pprint.pprint(flattened_results)

    logger.info(f"Fetched {len(flattened_results)} events")

    return flattened_results
