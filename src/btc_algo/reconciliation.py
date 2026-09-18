from __future__ import annotations

from dataclasses import dataclass

from btc_algo.domain import OrderStatus
from btc_algo.exchange import BinanceAdapter, ExchangeOrder
from btc_algo.repository import TradingRepository


@dataclass(frozen=True)
class ReconciliationReport:
    checked_orders: int
    mismatches: int
    unknown_exchange_orders: int


class Reconciler:
    """Reconcile locally persisted orders against exchange state after restart."""

    def __init__(self, exchange: BinanceAdapter, repository: TradingRepository) -> None:
        self.exchange = exchange
        self.repository = repository

    async def reconcile_symbol(self, symbol: str) -> ReconciliationReport:
        open_orders = await self.exchange.fetch_open_orders(symbol)
        mismatches = 0
        unknown = 0

        for exchange_order in open_orders:
            local = None
            if exchange_order.client_order_id:
                local = await self.repository.get_order_by_client_id(
                    exchange_order.client_order_id
                )

            if local is None:
                unknown += 1
                continue

            if local.status != exchange_order.status.value:
                mismatches += 1
                await self.repository.update_order(
                    local.client_order_id,
                    exchange_order_id=exchange_order.exchange_order_id,
                    status=exchange_order.status.value,
                )

        return ReconciliationReport(
            checked_orders=len(open_orders),
            mismatches=mismatches,
            unknown_exchange_orders=unknown,
        )
