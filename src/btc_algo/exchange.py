from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import ccxt.async_support as ccxt

from btc_algo.config import Settings
from btc_algo.domain import OrderSide, OrderStatus


@dataclass(frozen=True)
class ExchangeOrder:
    exchange_order_id: str
    client_order_id: str | None
    symbol: str
    side: OrderSide
    status: OrderStatus
    quantity: float
    filled_quantity: float
    average_fill_price: float | None
    updated_at: datetime


class BinanceAdapter:
    """CCXT Binance adapter for testnet/live order queries and submission.

    The adapter never enables live trading by itself. The caller must explicitly
    select TESTNET or LIVE and pass credentials.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if settings.mode.value not in {"testnet", "live"}:
            raise ValueError("BinanceAdapter requires TESTNET or LIVE mode")
        if not settings.exchange_api_key or not settings.exchange_api_secret:
            raise RuntimeError("Exchange API credentials are required")
        exchange_cls = getattr(ccxt, "binance")
        self.exchange = exchange_cls({
            "apiKey": settings.exchange_api_key,
            "secret": settings.exchange_api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        if settings.mode.value == "testnet":
            self.exchange.set_sandbox_mode(True)

    async def load_markets(self) -> None:
        await self.exchange.load_markets()

    async def fetch_order(self, exchange_order_id: str, symbol: str) -> ExchangeOrder:
        order = await self.exchange.fetch_order(exchange_order_id, symbol)
        return self._normalize(order)

    async def fetch_open_orders(self, symbol: str) -> list[ExchangeOrder]:
        orders = await self.exchange.fetch_open_orders(symbol)
        return [self._normalize(order) for order in orders]

    async def fetch_balance(self) -> dict:
        return await self.exchange.fetch_balance()

    async def create_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        client_order_id: str | None = None,
    ) -> ExchangeOrder:
        params = {}
        if client_order_id:
            params["newClientOrderId"] = client_order_id
        order = await self.exchange.create_order(
            symbol, "market", side.value, quantity, None, params
        )
        return self._normalize(order)

    async def cancel_order(self, exchange_order_id: str, symbol: str) -> ExchangeOrder:
        order = await self.exchange.cancel_order(exchange_order_id, symbol)
        return self._normalize(order)

    async def close(self) -> None:
        await self.exchange.close()

    def _normalize(self, order: dict) -> ExchangeOrder:
        status_map = {
            "open": OrderStatus.SUBMITTED,
            "closed": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELED,
            "expired": OrderStatus.EXPIRED,
            "rejected": OrderStatus.REJECTED,
        }
        status = status_map.get(order.get("status"), OrderStatus.UNKNOWN)
        side = OrderSide(order["side"])
        return ExchangeOrder(
            exchange_order_id=str(order["id"]),
            client_order_id=order.get("clientOrderId"),
            symbol=order["symbol"],
            side=side,
            status=status,
            quantity=float(order.get("amount") or 0),
            filled_quantity=float(order.get("filled") or 0),
            average_fill_price=(
                float(order["average"]) if order.get("average") is not None else None
            ),
            updated_at=datetime.now(timezone.utc),
        )
