from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from btc_algo.domain import OrderSide, OrderStatus


class ExecutionMode(StrEnum):
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"


@dataclass(frozen=True)
class ExecutionResult:
    client_order_id: str
    status: OrderStatus
    exchange_order_id: str | None = None
    filled_quantity: float = 0.0
    average_fill_price: float | None = None


class ExecutionEngine:
    """Order-state boundary. Live trading remains opt-in and is not implemented here."""

    def __init__(self, mode: ExecutionMode = ExecutionMode.PAPER, live_enabled: bool = False) -> None:
        if mode is ExecutionMode.LIVE and not live_enabled:
            raise RuntimeError("LIVE execution requires explicit live_enabled=True")
        self.mode = mode
        self.live_enabled = live_enabled
        self._orders: dict[str, ExecutionResult] = {}

    async def submit(self, *, client_order_id: str, symbol: str, side: OrderSide, quantity: float, price: float | None = None) -> ExecutionResult:
        if not client_order_id or not symbol or quantity <= 0:
            raise ValueError("client_order_id, symbol and positive quantity are required")
        existing = self._orders.get(client_order_id)
        if existing is not None:
            return existing
        if self.mode is ExecutionMode.LIVE:
            raise NotImplementedError("Live exchange submission is disabled until adapter and reconciliation are validated")
        result = ExecutionResult(client_order_id, OrderStatus.FILLED, filled_quantity=quantity, average_fill_price=price)
        self._orders[client_order_id] = result
        return result

    def get(self, client_order_id: str) -> ExecutionResult | None:
        return self._orders.get(client_order_id)
