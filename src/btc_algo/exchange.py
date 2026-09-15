from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import ccxt.async_support as ccxt

from .config import Settings, TradingMode
from .models import Order, OrderType, Side


class ExchangeError(RuntimeError):
    pass


class ExchangeAdapter(ABC):
    @abstractmethod
    async def ticker(self, symbol: str) -> dict[str, Any]: ...

    @abstractmethod
    async def create_order(self, order: Order) -> dict[str, Any]: ...

    @abstractmethod
    async def fetch_order(self, order: Order) -> dict[str, Any]: ...

    @abstractmethod
    async def close(self) -> None: ...


class CcxtExchange(ExchangeAdapter):
    def __init__(self, settings: Settings) -> None:
        exchange_cls = getattr(ccxt, "binance")
        self.exchange = exchange_cls(
            {
                "apiKey": settings.exchange_api_key,
                "secret": settings.exchange_api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            }
        )
        if settings.mode is TradingMode.TESTNET:
            self.exchange.set_sandbox_mode(True)

    async def ticker(self, symbol: str) -> dict[str, Any]:
        try:
            return await self.exchange.fetch_ticker(symbol)
        except Exception as exc:
            raise ExchangeError(f"ticker failed: {exc}") from exc

    async def create_order(self, order: Order) -> dict[str, Any]:
        try:
            params = {"newClientOrderId": order.client_order_id}
            return await self.exchange.create_order(
                order.symbol,
                order.order_type.value,
                order.side.value,
                order.quantity,
                order.price,
                params,
            )
        except Exception as exc:
            raise ExchangeError(f"order creation failed: {exc}") from exc

    async def fetch_order(self, order: Order) -> dict[str, Any]:
        if not order.exchange_order_id:
            raise ValueError("exchange_order_id is required for reconciliation")
        try:
            return await self.exchange.fetch_order(order.exchange_order_id, order.symbol)
        except Exception as exc:
            raise ExchangeError(f"order reconciliation failed: {exc}") from exc

    async def close(self) -> None:
        await self.exchange.close()
