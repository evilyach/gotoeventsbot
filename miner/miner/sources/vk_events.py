import asyncio
import json
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from miner.miner.custom_types import Currency, EventSchema, Format, Source
from miner.miner.exceptions import ApiChangedException

API_PAGE_ALL = "https://vk.company/ru/press/events/"
API_PAGE_BY_ID = "https://vk.company/ru{}"


def convert_date(x: str) -> datetime:
    return datetime.fromisoformat(x).replace(tzinfo=None)


def convert_format(formats: list[str]) -> Format:
    if "online" in formats and "offline" in formats:
        return Format.HYBRID
    if "online" in formats:
        return Format.ONLINE
    if "offline" in formats:
        return Format.OFFLINE
    return Format.UNKNOWN


async def get_desciption(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(API_PAGE_BY_ID.format(url))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag:
        raise ApiChangedException

    data = json.loads(script_tag.text)
    return data["props"]["pageProps"]["event"]["text"]


async def get_vk_events(client: httpx.AsyncClient) -> list[EventSchema]:
    response = await client.get(API_PAGE_ALL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag:
        raise ApiChangedException

    data = json.loads(script_tag.text)
    events = data["props"]["pageProps"]["publications"]

    events = [event for event in events if convert_date(event["starts"]) > datetime.now()]
    if not events:
        return []

    ids = [json["id"] for json in events]
    tasks = [get_desciption(client, json["public_url"]) for json in events]
    results = await asyncio.gather(*tasks)
    descriptions = dict(zip(ids, results))

    event_list = [
        EventSchema(
            {
                "id": f"vk-{json["id"]}",
                "source": Source.VK_EVENTS,
                "title": json["title"],
                "description": descriptions[json["id"]],
                "datetime": convert_date(json["starts"]),
                "format": Format.UNKNOWN,
                "city": None,
                "address": None,
                "price": 0,
                "currency": Currency.RUB,
                "url": API_PAGE_BY_ID.format(json["public_url"]),
                "image_url": json.get("image_header_cropped", None),
            }
        )
        for json in events
    ]

    return event_list
