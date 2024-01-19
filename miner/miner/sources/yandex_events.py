import asyncio
from datetime import datetime

import httpx

from miner.miner.custom_types import EventSchema, Format, Source

API_LINK_ALL = "https://events.yandex.ru/api/events?isUpcoming=true"
API_LINK_BY_ID = "https://events.yandex.ru/api/events/{}"
API_LINK_PAGE = "https://events.yandex.ru/events/{}"


def convert_date(x: str) -> datetime:
    return datetime.fromisoformat(x)


def convert_format(is_online: bool) -> Format:
    return Format.ONLINE if is_online else Format.OFFLINE


async def get_yandex_events(client: httpx.AsyncClient) -> list[EventSchema]:
    response = await client.get(API_LINK_ALL)
    response.raise_for_status()

    events = response.json()["rows"]
    if not events:
        return []

    tasks = [client.get(API_LINK_BY_ID.format(event.get("id"))) for event in events]
    results = await asyncio.gather(*tasks)
    map(lambda x: x.raise_for_status, results)

    data = [result.json() for result in results]

    event_list = [
        EventSchema(
            {
                "id": json["slug"],
                "source": Source.YANDEX_EVENTS,
                "title": json["title"],
                "description": json["description"],
                "datetime": convert_date(json["startDate"]),
                "format": convert_format(json["isOnline"]),
                "city": json["city"],
                "address": "; ".join(
                    location["place"] for location in json["locations"]
                ),
                "price": 0,
                "currency": None,
                "url": API_LINK_PAGE.format(json["slug"]),
                "image_url": json["image"],
            }
        )
        for json in data
    ]

    return event_list
