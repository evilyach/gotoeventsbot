import asyncio
import logging
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)


async def run_at(when: datetime, task: Callable) -> None:
    now = datetime.now()
    delay = (when - now).total_seconds()

    logging.info(f"Scheduler: waiting for {delay} seconds")
    await asyncio.sleep(delay)
    logging.info(f"Scheduler: running the task...")

    try:
        await task()
        logging.info(f"Scheduler: task completed!")
    except Exception as error:
        logging.error(f"Scheduler: error occured! {str(error)}")
