from datetime import datetime

import httpx

from miner.miner.custom_types import Currency, EventSchema, Format, Source

API_LINK_ALL = "https://meetup.tinkoff.ru/pwameetups/papi/getMeetups"
API_LINK_PAGE = "https://meetup.tinkoff.ru/event/{}"


def convert_date(x: float) -> datetime:
    return datetime.utcfromtimestamp(x / 1000.0)


def convert_format(format: str) -> Format:
    return {
        "OFFLINE": Format.OFFLINE,
        "HYBRID": Format.HYBRID,
        "ONLINE": Format.ONLINE,
    }[format]


async def get_tinkoff_events(client: httpx.AsyncClient) -> list[EventSchema]:
    response = await client.get(
        API_LINK_ALL, params={"sortBy": "nearestFirst", "isPassed": "false"}
    )
    response.raise_for_status()

    if not (events := response.json()["payload"]["payload"]["meetups"]):
        return []

    event_list = [
        EventSchema(
            {
                "id": json["id"],
                "source": Source.TINKOFF_EVENTS,
                "title": json["title"],
                "description": json["description"],
                "datetime": convert_date(json["dateStart"]),
                "format": convert_format(json["format"]),
                "city": json["city"]["name"],
                "address": f"{json["platform"]["address"]} - {json["platform"]["title"]}",
                "price": 0,
                "currency": Currency.RUB,
                "url": API_LINK_PAGE.format(json["url"]),
                "image_url": json["banners"]["imageGrid"],
            }
        )
        for json in events
    ]

    return event_list
