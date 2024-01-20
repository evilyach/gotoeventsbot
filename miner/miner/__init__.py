import logging
from datetime import date, datetime, time, timedelta

import typer

from miner.miner.helpers import async_typer
from miner.miner.scheduler import run_at
from miner.miner.tasks import mine_data

logging.basicConfig(format="%(levelname)s : %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.ERROR)


app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command()
@async_typer
async def once():
    logger.info("Running once...")

    await mine_data()


@app.command()
@async_typer
async def run():
    logger.info("Starting...")

    while True:
        try:
            when = datetime.combine(date.today() + timedelta(days=1), time(8, 00))
            await run_at(when, mine_data)
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    app()
