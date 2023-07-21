from bernard import layers as lyr
from bernard.engine.request import Request
from bernard.engine.triggers import BaseTrigger

from rocket_man.storage import HasLaunchedContext
from rocket_man.storage import context_store as cs


class ActionSrcTrigger(BaseTrigger):
    def __init__(self, request: Request, action: str):
        super().__init__(request)
        self.action = action

    async def rank(self) -> float:
        if not self.request.has_layer(lyr.Postback):
            # action did not come from a button
            return 0.0

        payload = self.request.get_layer(lyr.Postback).payload

        if payload.get("action") != self.action:
            # bad action
            return 0.0

        return 1.0


class MaybeHasLaunchedTrigger(ActionSrcTrigger):
    @cs.inject()
    async def rank(self, context: dict) -> float:
        rank = await super().rank()
        if rank == 0.0:
            return 0.0

        payload = self.request.get_layer(lyr.Postback).payload

        if payload.get("cond") is None:
            # must show the first frame
            return 0.0

        if context.get("step") is None:
            # missing mandatory step
            # did the context expire?
            return 1.0

        # payload is valid and context is not expired
        return 0.0


class HasLaunchedTrigger(ActionSrcTrigger):
    @cs.inject()
    async def rank(self, context: HasLaunchedContext) -> float:
        rank = await super().rank()
        if rank == 0.0:
            return 0.0

        payload = self.request.get_layer(lyr.Postback).payload

        cond = payload.get("cond")
        if cond is None:
            # must show the first frame
            return 1.0

        if cond not in ("ge", "lt"):
            # invalid payload
            return 0.0

        if context.get("step") is None:
            # missing mandatory step
            # did the context expire?
            return 0.0

        # payload is valid and context is not expired
        return 1.0
