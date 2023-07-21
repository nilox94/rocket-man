import random

from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr

from rocket_man.services import FrameXService
from rocket_man.states.base import RocketManState
from rocket_man.states.common import has_launched_or_goodbye
from rocket_man.storage import HasLaunchedContext
from rocket_man.storage import context_store as cs
from rocket_man.utils import escape_md_link


class HasLaunched(RocketManState):
    @page_view("/bot/has_launched")
    @cs.inject()
    async def handle(self, context: HasLaunchedContext) -> None:
        payload = self.request.get_layer(lyr.Postback).payload

        cond = payload.get("cond")
        if cond is None:
            await self._handle_initial(context)
        else:
            await self._handle_conditional(context, cond)

    async def _handle_initial(self, context):
        step = 1
        # choose a random image
        async with FrameXService() as fx:
            videos = await fx.list_videos()
        vid = random.choice(videos)

        context["video_name"] = video_name = vid.name
        lo, hi = 0, vid.frames

        await self._handle_step(context, lo, hi, video_name, step)

    async def _handle_conditional(self, context, cond):
        step = context["step"]
        lo = context["lo"]
        hi = context["hi"]
        mid = context["mid"]
        video_name = context["video_name"]

        if cond == "ge":
            hi = mid
        else:
            lo = mid + 1

        await self._handle_step(context, lo, hi, video_name, step)

    async def _handle_step(self, context, lo, hi, video_name, step):
        mid = (lo + hi) // 2

        frame_url = FrameXService.get_video_frame_url(video_name, mid)
        frame_url = escape_md_link(frame_url)

        if lo == hi:
            context.clear()
            self.send(
                lyr.Markdown(t("WIN", url=frame_url, step=step - 1)),
                has_launched_or_goodbye(),
            )
            return

        context["lo"] = lo
        context["hi"] = hi
        context["mid"] = mid
        context["step"] = step + 1

        self.send(
            lyr.Markdown(t("HAS_LAUNCHED", url=frame_url, step=step)),
            tgr.InlineKeyboard(
                [
                    [
                        tgr.InlineKeyboardCallbackButton(
                            text=t.YES,
                            payload={"action": "has_launched", "cond": "ge"},
                        ),
                        tgr.InlineKeyboardCallbackButton(
                            text=t.NO,
                            payload={"action": "has_launched", "cond": "lt"},
                        ),
                    ]
                ]
            ),
        )
