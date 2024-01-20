import pickle
from datetime import datetime

import httpx

from miner.miner.custom_types import Currency, EventSchema, Format, Source

API_LINK_ALL = "https://feeds.tildacdn.com/api/getfeed/?feeduid=617755803461"


def convert_date(x: str) -> datetime:
    return datetime.strptime(x, "%Y-%m-%d %H:%M")


def get_format_from_parts(s: str) -> Format:
    parts = s.split(",")

    for part in parts:
        if part.lower() == "online":
            return Format.ONLINE
        if part.lower() == "offline":
            return Format.OFFLINE

    return Format.UNKNOWN


def get_city_from_parts(s: str, cities: set) -> str | None:
    parts = s.split(",")

    for part in parts:
        if part in cities:
            return part

    return None


async def get_hackathon_rus_events(client: httpx.AsyncClient) -> list[EventSchema]:
    response = await client.get(API_LINK_ALL)
    response.raise_for_status()

    events = response.json()["posts"]
    if not events:
        return []

    with open("assets/cities.pkl", "rb") as city_pickle_jar:
        cities = pickle.load(city_pickle_jar)

        event_list = [
            EventSchema(
                {
                    "id": json["uid"],
                    "source": Source.HACKATHON_RUS_EVENTS,
                    "title": json["title"],
                    "description": json["descr"],
                    "datetime": convert_date(json["date"]),
                    "format": get_format_from_parts(json["parts"]),
                    "city": get_city_from_parts(json["parts"], cities),
                    "address": None,
                    "price": 0,
                    "currency": Currency.RUB,
                    "url": json["url"],
                    "image_url": json["image"],
                }
            )
            for json in events
            if convert_date(json["date"]) > datetime.now()
        ]

    return event_list
