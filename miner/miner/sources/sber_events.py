import asyncio
from collections import namedtuple
from datetime import datetime

import httpx

from miner.miner.custom_types import EventSchema, Format, Source

API_LINK_ALL = "https://developers.sber.ru/kak-v-sbere/_next/data/aVzv0q0D3b7EtWOABamwf/events.json"
API_LINK_BY_ID = (
    "https://developers.sber.ru/kak-v-sbere/_next/data/aVzv0q0D3b7EtWOABamwf/{}.json"
)
API_LINK_PAGE = (
    "https://developers.sber.ru/kak-v-sbere/_next/data/aVzv0q0D3b7EtWOABamwf/{}"
)


InitialDataValue = namedtuple("InitialDataValue", ["date", "url", "place"])


def convert_date(x: str) -> datetime:
    return datetime.strptime(x, "%Y-%m-%d")


def get_format_from_place(place: str) -> Format:
    return Format.ONLINE if place == "онлайн" else Format.OFFLINE


def get_city_from_place(place: str) -> str | None:
    return None if place == "онлайн" else place.split(", ")[0]


def get_address_from_place(place: str) -> str | None:
    return None if place == "онлайн" else place


async def get_sber_events(client: httpx.AsyncClient) -> list[EventSchema] | None:
    response = await client.get(API_LINK_ALL)
    response.raise_for_status()

    events = [
        event
        for event in response.json()["pageProps"]["page"]["MainContent"][0]["cards"]
        if convert_date(event["StartDate"]) > datetime.now()
    ]
    if not events:
        return []

    initial_data = {
        event["slug"]: InitialDataValue(
            date=convert_date(event["StartDate"]),
            url=API_LINK_PAGE.format(event["EventUrl"]),
            place=event["Place"],
        )
        for event in events
    }

    tasks = [client.get(API_LINK_BY_ID.format(event["EventUrl"])) for event in events]
    results = await asyncio.gather(*tasks)
    map(lambda x: x.raise_for_status, results)

    data = [result.json()["pageProps"]["page"] for result in results]

    event_list = [
        EventSchema(
            {
                "id": json["slug"],
                "source": Source.SBER_EVENTS,
                "title": json["Title"],
                "description": json.get("Description", None),
                "datetime": initial_data[json["slug"]].date,
                "format": get_format_from_place(initial_data[json["slug"]].place),
                "city": get_city_from_place(initial_data[json["slug"]].place),
                "address": get_address_from_place(initial_data[json["slug"]].place),
                "price": 0,
                "currency": None,
                "url": initial_data[json["slug"]].url,
                "image_url": json["Image"]["url"],
            }
        )
        for json in data
    ]

    return event_list
