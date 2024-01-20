import asyncio
from datetime import datetime
from enum import Enum
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup

from miner.miner.custom_types import EventSchema, Format, Source
from miner.miner.helpers import flatten_2d_container

API_PAGE_ALL = "https://events.sk.ru"


class Category(Enum):
    BUSINESS = 2
    EDUCATION = 3
    INVESTMENTS = 4


months = {
    "Января": 1,
    "Февраля": 2,
    "Марта": 3,
    "Апреля": 4,
    "Мая": 5,
    "Июня": 6,
    "Июля": 7,
    "Августа": 8,
    "Сентября": 9,
    "Октября": 10,
    "Ноября": 11,
    "Декабря": 12,
}


def convert_date(x: str) -> datetime:
    return datetime.strptime(x, "%d %M %Y").replace(year=datetime.now().year)


def get_date(x: str) -> datetime:
    date_str = " ".join(d for d in [d.strip() for d in x.splitlines()] if d != "")
    dates = date_str.split(" - ")

    if len(dates) == 2:
        date = dates[0] + " " + dates[1].split()[-1]
    else:
        date = dates[0]

    for name, num in months.items():
        date = date.replace(name, str(num))

    return convert_date(date)


def get_city_from_address(address: str | None) -> str | None:
    return address.split(", ")[0] if address else None


def generate_id(url: str) -> str:
    base_url = urlsplit(url).netloc.replace(".", "-")
    return f"sk-{base_url}"


def get_image_url(image_url: str) -> str:
    return f"{API_PAGE_ALL}{image_url}"


async def get_desciption(client: httpx.AsyncClient, url: str) -> str | None:
    response = await client.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    if not (paragraphs := soup.find("div", class_="b-content")):
        return None

    return paragraphs.get_text(strip=True)


async def get_event(client: httpx.AsyncClient, item) -> EventSchema:
    title = item.find("div", class_="category-events__item-name").get_text(strip=True)
    date = item.find("div", class_="category-events__item-dates").get_text(strip=True)
    url = item.find("a", class_="category-events__detail-link")["href"]
    image_url = item.find("img", class_="category-events__item-img")["data-src"]

    try:
        address = None
        place = item.find("div", class_="category-events__item-source").get_text(
            strip=True
        )
    except Exception:
        place = address = item.find(
            "div", class_="category-events__item-address"
        ).get_text(strip=True)

    if place == "Онлайн":
        address = None
        format = Format.ONLINE
    else:
        address = item.find("div", class_="category-events__item-address").get_text(
            strip=True
        )
        format = Format.OFFLINE

    return EventSchema(
        {
            "id": generate_id(url),
            "source": Source.SK_EVENTS,
            "title": title,
            "description": await get_desciption(client, url),
            "datetime": get_date(date),
            "format": format,
            "city": get_city_from_address(address)
            if format == Format.OFFLINE
            else None,
            "address": address,
            "price": None,
            "currency": None,
            "url": url,
            "image_url": get_image_url(image_url),
        }
    )


async def get_sk_events_for_category(
    client: httpx.AsyncClient, category: Category
) -> list[EventSchema]:
    response = await client.get(API_PAGE_ALL, params={"category": category.value})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    event_divs = soup.find_all("div", class_="category-events__item")

    tasks = [get_event(client, event_div) for event_div in event_divs]
    return await asyncio.gather(*tasks)


async def get_sk_events(client: httpx.AsyncClient) -> list[EventSchema]:
    tasks = [get_sk_events_for_category(client, category) for category in Category]
    return flatten_2d_container(await asyncio.gather(*tasks))
