import asyncio
import logging
import pprint

import httpx

from miner.miner.sources.hackathon_rus_events import get_hackathon_rus_events
from miner.miner.sources.illusion_events import get_illusion_events
from miner.miner.sources.sber_events import get_sber_events
from miner.miner.sources.tinkoff_events import get_tinkoff_events
from miner.miner.sources.yandex_events import get_yandex_events

logger = logging.getLogger(__name__)


def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


async def mine_data():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            get_hackathon_rus_events(client),
            get_illusion_events(client),
            get_sber_events(client),
            get_tinkoff_events(client),
            get_yandex_events(client),
        )

    flattened_results = flatten_comprehension(results)

    pprint.pprint(flattened_results)
    logger.info(f"Fetched {len(flattened_results)} events")
