import asyncio
import logging
from datetime import date, datetime, time, timedelta
from typing import NoReturn

from miner.miner.scheduler import run_at
from miner.miner.tasks import mine_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> NoReturn:
    logger.info("Starting...")

    while True:
        when = datetime.combine(date.today() + timedelta(days=1), time(8, 00))

        print(when)

        await run_at(when, mine_data)


if __name__ == "__main__":
    asyncio.run(main())
