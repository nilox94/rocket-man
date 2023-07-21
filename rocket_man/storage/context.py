from functools import wraps
from typing import AsyncGenerator, Generic

from bernard.core.health_check import HealthCheckFail
from bernard.engine.state import BaseState
from bernard.engine.triggers import BaseTrigger
from bernard.storage.context.base import ContextContextManager

from rocket_man.storage.redis import Context, RedisMixin


class BaseContextStore:
    """
    Defines the interface of a context store.

    The context store stores a dictionary object in whichever way it wants (by
    example in a Redis database). Each context is a plain dictionary object.
    Each context is created for one conversation and expires after X seconds.

    The implementer of context store must implement a `_get()` and a `_set()`
    method.

    For a user of this class, the main entry point is `inject()`.
    """

    def __init__(self, name, **kwargs):
        # noinspection PyArgumentList
        super().__init__(**kwargs)

        self.name = name
        self._init_done = False

    async def async_init(self) -> None:
        pass

    async def ensure_async_init(self) -> None:
        """
        This allows to lazily do the async init
        """

        if not self._init_done:
            await self.async_init()
            self._init_done = True

    async def _get(self, key: str) -> Context:
        """
        Implement this as a method to get the context for the given key.
        """
        raise NotImplementedError

    async def _set(self, key: str, data: Context) -> None:
        """
        Implement this as a method to set the context at the given key.
        """
        raise NotImplementedError

    def open(self, key: str) -> ContextContextManager:
        """
        Opens a context using the a Python context manager.

        The `key` is the arbitrary key identifying the context.
        """
        return ContextContextManager(key, self)

    def inject(
        self,
        require: list[str] | None = None,
        fail: str = "missing_context",
        var_name: str = "context",
    ):
        """
        This is a decorator intended to be used on states (and actually only
        work on state handlers).

        The `require` argument is a list of keys to be checked in the context.
        If at least one of them is missing, then instead of calling the handler
        another method will be called. By default the method is
        `missing_context` but it can be configured using the `fail` argument.

        The context will be injected into the handler as a keyword arg. By
        default, the arg is expected to be named `context` but you can change
        it to anything you'd like using `var_name`.

        See `create_context_store()` for a full example.
        """

        def decorator(func):
            async def health_check(cls) -> AsyncGenerator[HealthCheckFail, None]:
                if not callable(getattr(cls, fail, None)):
                    yield HealthCheckFail(
                        "00001",
                        f'State "{cls.__name__}" has no method "{fail}" to '
                        f"fall back to if required attributes are missing "
                        f"from the context.",
                    )

            if require:
                func.health_check = health_check

            @wraps(func)
            async def wrapper(state: BaseState | BaseTrigger, **kwargs):
                conv_id = state.request.conversation.id
                key = f"context::{self.name}::{conv_id}"

                x = self.open(key)
                async with x as context:
                    for item in require or []:
                        if item not in context:
                            return await getattr(state, fail)(state, **kwargs)

                    kwargs[var_name] = context
                    return await func(state, **kwargs)

            return wrapper

        return decorator


class ContextStore(RedisMixin, BaseContextStore, Generic[Context]):
    """
    Store the context as a serialized JSON inside Redis. It's made to be
    compatible with the register storage, if using the same Redis DB.
    """
