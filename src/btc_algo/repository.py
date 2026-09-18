from __future__ import annotations

from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from btc_algo.db_models import FillRecord, OrderRecord

class TradingRepository:
    def __init__(self, session: AsyncSession): self.session = session
    async def get_order_by_client_id(self, client_order_id: str):
        result = await self.session.execute(select(OrderRecord).where(OrderRecord.client_order_id == client_order_id))
        return result.scalar_one_or_none()
    async def create_order(self, **values):
        existing = await self.get_order_by_client_id(values["client_order_id"])
        if existing is not None: return existing
        order = OrderRecord(**values); self.session.add(order)
        try: await self.session.flush()
        except IntegrityError:
            await self.session.rollback(); existing = await self.get_order_by_client_id(values["client_order_id"])
            if existing is None: raise
            return existing
        return order
    async def update_order(self, client_order_id: str, **values):
        order = await self.get_order_by_client_id(client_order_id)
        if order is None: return None
        for key, value in values.items(): setattr(order, key, value)
        await self.session.flush(); return order
    async def record_fill(self, **values):
        result = await self.session.execute(select(FillRecord).where(FillRecord.exchange_trade_id == values["exchange_trade_id"]))
        existing = result.scalar_one_or_none()
        if existing is not None: return existing
        fill = FillRecord(**values); self.session.add(fill)
        try: await self.session.flush()
        except IntegrityError:
            await self.session.rollback(); result = await self.session.execute(select(FillRecord).where(FillRecord.exchange_trade_id == values["exchange_trade_id"]))
            existing = result.scalar_one_or_none()
            if existing is None: raise
            return existing
        return fill
