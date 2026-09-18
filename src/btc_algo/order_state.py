from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4

from btc_algo.domain import OrderSide, OrderStatus
from btc_algo.exchange import BinanceAdapter, ExchangeOrder
from btc_algo.repository import TradingRepository


class ExecutionState(StrEnum):
    NEW = "new"
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ManagedOrder:
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    state: ExecutionState
    exchange_order_id: str | None = None
    filled_quantity: float = 0.0
    average_fill_price: float | None = None


class OrderStateMachine:
    """Persistent order lifecycle with idempotent submission and reconciliation."""

    def __init__(self, exchange: BinanceAdapter, repository: TradingRepository) -> None:
        self.exchange = exchange
        self.repository = repository

    async def submit(
        self,
        *,
        symbol: str,
        side: OrderSide,
        quantity: float,
        client_order_id: str | None = None,
    ) -> ManagedOrder:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        client_id = client_order_id or f"btc-{uuid4().hex}"
        existing = await self.repository.get_order_by_client_id(client_id)
        if existing is not None:
            return ManagedOrder(
                client_id,
                existing.symbol,
                OrderSide(existing.side),
                float(existing.quantity),
                ExecutionState(existing.status),
                existing.exchange_order_id,
            )

        await self.repository.create_order(
            client_order_id=client_id,
            symbol=symbol,
            side=side.value,
            status=ExecutionState.SUBMITTING.value,
            quantity=quantity,
        )

        try:
            result = await self.exchange.create_market_order(
                symbol, side, quantity, client_order_id=client_id
            )
        except Exception:
            # An ambiguous network failure must not trigger a blind retry.
            # Reconciliation establishes whether the exchange accepted it.
            await self.repository.update_order(
                client_id, status=ExecutionState.UNKNOWN.value
            )
            raise

        state = self._state(result)
        await self.repository.update_order(
            client_id,
            exchange_order_id=result.exchange_order_id,
            status=state.value,
        )
        return ManagedOrder(
            client_id,
            symbol,
            side,
            quantity,
            state,
            result.exchange_order_id,
            result.filled_quantity,
            result.average_fill_price,
        )

    async def reconcile(self, client_order_id: str, symbol: str) -> ManagedOrder | None:
        local = await self.repository.get_order_by_client_id(client_order_id)
        if local is None or not local.exchange_order_id:
            return None

        result = await self.exchange.fetch_order(local.exchange_order_id, symbol)
        state = self._state(result)
        await self.repository.update_order(
            client_order_id,
            status=state.value,
        )
        return ManagedOrder(
            client_order_id,
            symbol,
            OrderSide(local.side),
            float(local.quantity),
            state,
            result.exchange_order_id,
            result.filled_quantity,
            result.average_fill_price,
        )

    @staticmethod
    def _state(order: ExchangeOrder) -> ExecutionState:
        mapping = {
            OrderStatus.SUBMITTED: ExecutionState.SUBMITTED,
            OrderStatus.PARTIALLY_FILLED: ExecutionState.PARTIALLY_FILLED,
            OrderStatus.FILLED: ExecutionState.FILLED,
            OrderStatus.CANCELED: ExecutionState.CANCELED,
            OrderStatus.REJECTED: ExecutionState.REJECTED,
            OrderStatus.EXPIRED: ExecutionState.EXPIRED,
        }
        return mapping.get(order.status, ExecutionState.UNKNOWN)
