from bernard import layers as lyr
from bernard.engine.triggers import BaseTrigger

from rocket_man.store import HasLaunchedContext
from rocket_man.store import context_store as cs


class MaybeHasLaunchedTrigger(BaseTrigger):
    @cs.inject()
    async def rank(self, context: dict) -> float:
        if not self.request.has_layer(lyr.Postback):
            # action did not come from a button
            return 0.0

        payload = self.request.get_layer(lyr.Postback).payload

        if payload.get("action") != "has_launched":
            # action is not "has_launched"
            return 0.0

        if payload.get("cond") is None:
            # must show the first frame
            return 0.0

        if context.get("step") is None:
            # missing mandatory step
            # did the context expire?
            return 1.0

        # payload is valid and context is not expired
        return 0.0


class HasLaunchedTrigger(BaseTrigger):
    @cs.inject()
    async def rank(self, context: HasLaunchedContext) -> float:
        if not self.request.has_layer(lyr.Postback):
            # action did not come from a button
            return 0.0

        payload = self.request.get_layer(lyr.Postback).payload

        if payload.get("action") != "has_launched":
            # action is not "has_launched"
            return 0.0

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
