import random

from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.engine import BaseState
from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr

from rocket_man.services import FrameXService
from rocket_man.store import HasLaunchedContext
from rocket_man.store import context_store as cs
from rocket_man.utils import escape_md_link


class RocketManState(BaseState):
    """
    Root class for Rocket Man.

    Here you must implement "error" and "confused" to suit your needs. They
    are the default functions called when something goes wrong. The ERROR and
    CONFUSED texts are defined in `i18n/en/responses.csv`.
    """

    @page_view("/bot/error")
    async def error(self) -> None:
        """
        This happens when something goes wrong (it's the equivalent of the
        HTTP error 500).
        """
        self.send(lyr.Text(t.ERROR))

    @page_view("/bot/confused")
    async def confused(self) -> None:
        """
        This is called when the user sends a message that triggers no
        transitions.
        """
        self.send(lyr.Text(t.CONFUSED))

    async def handle(self) -> None:
        raise NotImplementedError


class Hello(RocketManState):
    """
    Example "Hello" state, to show you how it's done. You can remove it.

    Please note the @page_view decorator that allows to track the viewing of
    this page using the analytics provider set in the configuration. If there
    is no analytics provider, nothing special will happen and the handler
    will be called as usual.
    """

    @page_view("/bot/hello")
    async def handle(self):
        self.send(
            lyr.Text(t.HELLO),
            has_launched_or_goodbye(),
        )


class Goodbye(RocketManState):
    @page_view("/bot/goodbye")
    async def handle(self):
        self.send(lyr.Text(t.GOODBYE))


def has_launched_or_goodbye():
    return tgr.InlineKeyboard(
        [
            [
                tgr.InlineKeyboardCallbackButton(
                    text=t.YES,
                    payload={"action": "has_launched"},
                ),
                tgr.InlineKeyboardCallbackButton(
                    text=t.NO,
                    payload={"action": "goodbye"},
                ),
            ]
        ]
    )


class MaybeHasLaunched(RocketManState):
    """ "
    The user wants to see a picture of the rocket launch,
    but we might have lost track of where they are in the process.
    e.g. context has expired.
    """

    @page_view("/bot/maybe_has_launched")
    @cs.inject()
    async def handle(self, context: HasLaunchedContext) -> None:
        self.send(
            lyr.Text(t.MAYBE_HAS_LAUNCHED),
            has_launched_or_goodbye(),
        )


class HasLaunched(RocketManState):
    """
    Ask the user if the rocket has launched yet.
    """

    @page_view("/bot/has_launched")
    @cs.inject()
    async def handle(self, context: HasLaunchedContext) -> None:
        payload = self.request.get_layer(lyr.Postback).payload

        cond = payload.get("cond")
        if cond is not None:
            step = context["step"]
            lo = context["lo"]
            hi = context["hi"]
            mid = context["mid"]
            video_name = context["video_name"]

            if cond == "ge":
                hi = mid
            else:
                lo = mid + 1
        else:
            step = 1
            # choose a random image
            async with FrameXService() as fx:
                videos = await fx.list_videos()
            vid = random.choice(videos)

            context["video_name"] = video_name = vid.name
            lo, hi = 0, vid.frames

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
