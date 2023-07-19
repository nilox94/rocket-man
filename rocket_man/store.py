from typing import Generic, Mapping, TypedDict, TypeVar

import ujson
from bernard.conf import settings
from bernard.storage.context import RedisContextStore
from redis.asyncio import Redis

Context = TypeVar("Context", bound=Mapping)


class ContextStore(RedisContextStore, Generic[Context]):
    """
    Store the context as a serialized JSON inside Redis. It's made to be
    compatible with the register storage, if using the same Redis DB.

    Example:
        class S0Context(TypedDict):
            a: int
            b: int | None
        cs = ContextStore[S0Context](name="s0", ttl=5*60)
    """

    redis: Redis
    ttl: int

    def __init__(
        self, name: str = "default", ttl: int = settings.CONTEXT_DEFAULT_TTL, params: dict = settings.REDIS_PARAMS
    ):
        """
        Create a context store with the given parameters.

        :param name: The name of the context store.
        :param ttl: The TTL of the context store.
        :param params: Redis store params (see `bernard.storage.redis.BaseRedisStore`)
        """
        super().__init__(name=name, ttl=ttl, **params)

    async def _get(self, key: str) -> Context:
        return await super()._get(key)

    async def _set(self, key: str, data: Context) -> None:
        await self.redis.set(key, ujson.dumps(data), ex=self.ttl)


class HasLaunchedContext(TypedDict):
    step: int
    lo: int | None
    hi: int | None
    mid: int | None
    video_name: str | None


context_store = ContextStore[HasLaunchedContext](name="has_launched")
