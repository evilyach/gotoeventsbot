from datetime import datetime
from enum import Enum, auto
from typing import TypedDict


class Source(Enum):
    YANDEX_EVENTS = auto()
    SBER_EVENTS = auto()
    HACKATHON_RUS_EVENTS = auto()
    TINKOFF_EVENTS = auto()
    ILLUSION_EVENTS = auto()
    VK_CLOUD_EVENTS = auto()
    VK_EVENTS = auto()
    SK_EVENTS = auto()


class Format(Enum):
    OFFLINE = auto()
    HYBRID = auto()
    ONLINE = auto()
    UNKNOWN = auto()


class Currency(Enum):
    RUB = auto()


class EventSchema(TypedDict):
    id: str
    source: Source
    title: str
    description: str | None
    datetime: datetime | None
    format: Format
    city: str | None
    address: str | None
    price: int | None
    currency: Currency | None
    url: str
    image_url: str | None
