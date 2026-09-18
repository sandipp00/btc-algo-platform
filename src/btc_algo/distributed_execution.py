from __future__ import annotations

import json
from dataclasses import dataclass

from btc_algo.domain import OrderSide
from btc_algo.exchange import BinanceAdapter
from btc_algo.redis_bus import RedisBus
from btc_algo.repository import TradingRepository


@dataclass(frozen=True)
class SubmissionDecision:
    submitted: bool
    reason: str


class DistributedOrderGuard:
    """Coordinates order submission across multiple workers."""

    def __init__(self, redis: RedisBus, exchange: BinanceAdapter, repository: TradingRepository) -> None:
        self.redis = redis
        self.exchange = exchange
        self.repository = repository

    async def submit_once(
        self,
        *,
        client_order_id: str,
        symbol: str,
        side: OrderSide,
        quantity: float,
    ) -> SubmissionDecision:
        async with self.redis.order_lock(client_order_id) as acquired:
            if not acquired:
                return SubmissionDecision(False, "order_lock_unavailable")

            existing = await self.repository.get_order_by_client_id(client_order_id)
            if existing is not None and existing.exchange_order_id:
                return SubmissionDecision(False, "already_submitted")

            await self.repository.create_order(
                client_order_id=client_order_id,
                symbol=symbol,
                side=side.value,
                status="submitting",
                quantity=quantity,
            )

            try:
                order = await self.exchange.create_market_order(
                    symbol, side, quantity, client_order_id
                )
            except Exception:
                await self.repository.update_order(
                    client_order_id, status="unknown"
                )
                raise

            await self.repository.update_order(
                client_order_id,
                exchange_order_id=order.exchange_order_id,
                status=order.status.value,
            )
            await self.redis.publish(
                "btc-algo:orders",
                json.dumps({
                    "event": "order_submitted",
                    "client_order_id": client_order_id,
                    "exchange_order_id": order.exchange_order_id,
                    "symbol": symbol,
                    "status": order.status.value,
                }),
            )
            return SubmissionDecision(True, "submitted")
