from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone

import ccxt.async_support as ccxt


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataClient:
    """Resilient CCXT market-data client. No trading methods are exposed here."""

    def __init__(self, exchange_id: str = "binance") -> None:
        exchange_cls = getattr(ccxt, exchange_id)
        self.exchange = exchange_cls({"enableRateLimit": True})

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> list[Candle]:
        rows = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        return [
            Candle(
                timestamp=datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in rows
        ]

    async def ticker(self, symbol: str) -> dict[str, float | datetime]:
        ticker = await self.exchange.fetch_ticker(symbol)
        return {
            "bid": float(ticker["bid"]),
            "ask": float(ticker["ask"]),
            "last": float(ticker["last"]),
            "timestamp": datetime.now(timezone.utc),
        }

    async def close(self) -> None:
        await self.exchange.close()

    async def __aenter__(self) -> "MarketDataClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
