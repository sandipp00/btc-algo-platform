from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(StrEnum):
    NEW = "new"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Signal:
    symbol: str
    side: Side
    timestamp: datetime
    stop_price: float
    reason: str


@dataclass
class Order:
    client_order_id: str
    symbol: str
    side: Side
    order_type: OrderType
    quantity: float
    price: float | None = None
    status: OrderStatus = OrderStatus.NEW
    exchange_order_id: str | None = None
    filled_quantity: float = 0.0
    average_fill_price: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
