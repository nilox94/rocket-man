from typing import TypedDict

from rocket_man.storage.context import ContextStore
from rocket_man.storage.redis import Context
from rocket_man.storage.register import RegisterStore


class HasLaunchedContext(TypedDict):
    step: int
    lo: int | None
    hi: int | None
    mid: int | None
    video_name: str | None


context_store = ContextStore[HasLaunchedContext](name="has_launched")
