import asyncio
from typing import Mapping, TypeVar

import ujson
from bernard.conf import settings
from redis.asyncio import Redis

Context = TypeVar("Context", bound=Mapping)


class RedisMixin:
    redis: Redis

    def __init__(
        self,
        redis_url: str | None = None,
        ttl: int | None = None,
        max_connections: int = 10,
        content_prefix: str = "",
        lock_prefix: str = "",
        **kwargs,
    ):
        """
        Create a context store with the given parameters.

        :param redis_url: The redis url to connect to.
        :param max_connections: maximum number of connections alive
        """
        super().__init__(**kwargs)
        self.redis_url = redis_url or settings.REDIS_PARAMS["redis_url"]
        self.ttl = ttl or settings.REDIS_PARAMS["ttl"]
        self.max_connections = max_connections
        self.content_prefix = content_prefix
        self.lock_prefix = lock_prefix

    async def async_init(self):
        """
        Handle here the asynchronous part of the init.
        """
        self.redis = await Redis.from_url(
            self.redis_url,
            max_connections=self.max_connections,
        )

    def lock_key(self, key: str) -> str:
        """
        Compute the internal lock key for the specified key
        """
        return f"{self.lock_prefix}{key}"

    def content_key(self, key: str) -> str:
        """
        Compute the internal content key for the specified key
        """
        return f"{self.content_prefix}{key}"

    async def _start(self, key: str) -> None:
        """
        Start the lock.

        Here we use a SETNX-based algorithm. It's quite shitty, change it.
        """
        for _ in range(0, 1000):
            just_set = await self.redis.setnx(self.lock_key(key), "")

            if just_set:
                break

            await asyncio.sleep(settings.REDIS_POLL_INTERVAL)

    async def _finish(self, key: str) -> None:
        """
        Remove the lock.
        """
        await self.redis.delete(self.lock_key(key))

    async def _get(self, key: str) -> Context:
        """
        Get the value for the key. It is automatically deserialized from JSON
        and returns an empty dictionary by default.
        """
        value = await self.redis.get(self.content_key(key))
        if value is None:
            return {}  # type: ignore[return-value]
        return ujson.loads(value)

    async def _set(self, key: str, data: Context) -> None:
        """
        Set the value for the key.
        """
        await self.redis.set(self.content_key(key), ujson.dumps(data), ex=self.ttl)

    async def _replace(self, key: str, data: Context) -> None:
        """
        Replace content with a new value.
        """
        await self._set(key, data)
