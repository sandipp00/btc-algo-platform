from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .config import Settings, TradingMode
from .exchange import ExchangeAdapter
from .models import Order, OrderType, Side


class ExecutionEngine:
    """Single entry point for order submission. Live mode is explicitly gated."""

    def __init__(self, settings: Settings, exchange: ExchangeAdapter) -> None:
        self.settings = settings
        self.exchange = exchange
        self._submitted: set[str] = set()

    async def submit_market(self, symbol: str, side: Side, quantity: float) -> Order:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.settings.validate_live_gate()
        if self.settings.mode not in (TradingMode.TESTNET, TradingMode.LIVE):
            raise RuntimeError("exchange execution is disabled outside testnet/live modes")

        client_order_id = f"btc-{uuid4().hex}"
        if client_order_id in self._submitted:
            raise RuntimeError("duplicate client order id")
        order = Order(
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            created_at=datetime.now(timezone.utc),
        )
        self._submitted.add(client_order_id)
        try:
            result = await self.exchange.create_order(order)
        except Exception:
            self._submitted.discard(client_order_id)
            raise
        order.exchange_order_id = str(result.get("id")) if result.get("id") is not None else None
        return order
