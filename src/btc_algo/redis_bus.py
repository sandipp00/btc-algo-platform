from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from redis.asyncio import Redis
from redis.exceptions import LockError


class RedisBus:
    """Redis-backed distributed lock and lightweight event bus."""

    def __init__(self, url: str) -> None:
        self.client: Redis = Redis.from_url(url, decode_responses=True)

    async def ping(self) -> bool:
        return bool(await self.client.ping())

    @asynccontextmanager
    async def order_lock(self, client_order_id: str, timeout: int = 30) -> AsyncIterator[bool]:
        lock = self.client.lock(f"btc-algo:order:{client_order_id}", timeout=timeout, blocking_timeout=5)
        acquired = await lock.acquire()
        try:
            yield acquired
        finally:
            if acquired:
                try:
                    await lock.release()
                except LockError:
                    pass

    async def publish(self, channel: str, payload: str) -> int:
        return int(await self.client.publish(channel, payload))

    async def close(self) -> None:
        await self.client.aclose()
