import asyncio
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from miner.miner.custom_types import Currency, EventSchema, Format, Source

API_LINK_ALL = "https://illusion-cinema.ru/events/"
API_LINK_BY_ID = "https://illusion-cinema.ru/{}/"


def convert_date(x: str) -> datetime:
    return datetime.strptime(x, "%d.%m").replace(year=datetime.now().year)


def get_date(x: str) -> datetime | None:
    try:
        dates = x.split(" - ")
        return convert_date(dates[0])
    except Exception:
        return None


def generate_id(url_path: str) -> str:
    return f"illusion-{url_path}"


def get_url(url_path: str) -> str:
    return API_LINK_BY_ID.format(url_path)


def get_image_url(string: str) -> str:
    start = string.find("url('") + len("url('")
    end = string.find("');", start)

    return f"https:{string[start:end]}"


async def get_desciption(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")

    return paragraphs[0].get_text(strip=True)


async def get_event(client: httpx.AsyncClient, div) -> EventSchema | None:
    date = get_date(div.find("span", class_="event_date").get_text(strip=True))
    if date and date < datetime.now():
        return

    title = div.find("label").get_text(strip=True)
    url_path = div.find("a")["href"].strip()[1:-1]
    image_url = div.find("a")["style"].strip()
    url = get_url(url_path)

    return EventSchema(
        {
            "id": generate_id(url_path),
            "source": Source.ILLUSION_EVENTS,
            "title": title,
            "description": await get_desciption(client, url),
            "datetime": date,
            "format": Format.OFFLINE,
            "city": "Москва",
            "address": "Котельническая набережная, 1/15 - Кинотеатр Иллюзион",
            "price": None,
            "currency": Currency.RUBLE,
            "url": url,
            "image_url": get_image_url(image_url),
        }
    )


async def get_illusion_events(client: httpx.AsyncClient) -> list[EventSchema]:
    response = await client.get(API_LINK_ALL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    event_divs = soup.find_all("div", class_="im-view img")

    tasks = [get_event(client, event_div) for event_div in event_divs]
    events = await asyncio.gather(*tasks)

    return [event for event in events if event]
