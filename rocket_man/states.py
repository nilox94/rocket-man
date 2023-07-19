import random

from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.engine import BaseState
from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr

from rocket_man.services import FrameXService
from rocket_man.store import HasLaunchedContext
from rocket_man.store import context_store as cs
from rocket_man.utils import md_link


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
            lyr.Text(
                "\n".join(
                    [
                        "Hello!",
                        "I'd like to show you pictures of a rocket launch and ask you if it has launched yet.",
                        "What do you say?",
                    ]
                )
            ),
            has_launched_or_goodbye(),
        )


class Goodbye(RocketManState):
    @page_view("/bot/goodbye")
    async def handle(self):
        self.send(
            lyr.Text(
                "\n".join(
                    [
                        "Goodbye!",
                        "I hope you enjoyed the rocket launch.",
                        "See you next time!",
                    ]
                )
            ),
        )


def has_launched_or_goodbye():
    return tgr.InlineKeyboard(
        [
            [
                tgr.InlineKeyboardCallbackButton(
                    text="YAY",
                    payload={"action": "has_launched"},
                ),
                tgr.InlineKeyboardCallbackButton(
                    text="NAY",
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
        print("Maybe Has Launched?")
        self.send(
            lyr.Text(
                "\n".join(
                    [
                        "It looks like you were in the middle of something, but I forgot what.",
                        "Would you like to start over?",
                    ]
                )
            ),
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
                lo, hi = 0, vid.frames
                video_name = vid.name
                context["video_name"] = video_name

        step += 1
        if lo == hi:
            context.clear()
            self.send(
                lyr.Text(f"Thanks!\nYou helped me find the right frame in {step} steps!\nWanna try again?"),
                has_launched_or_goodbye(),
            )
            return

        context["lo"] = lo
        context["hi"] = hi
        context["mid"] = mid = (lo + hi) // 2
        context["step"] = step

        frame_url = FrameXService.get_video_frame_url(video_name, mid)
        self.send(
            lyr.Markdown(f"Has {md_link(frame_url, 'the rocket')} launched yet?"),
            tgr.InlineKeyboard(
                [
                    [
                        tgr.InlineKeyboardCallbackButton(
                            text="YES",
                            payload=dict(
                                action="has_launched",
                                cond="ge",
                            ),
                        ),
                        tgr.InlineKeyboardCallbackButton(
                            text="NO",
                            payload=dict(
                                action="has_launched",
                                cond="lt",
                            ),
                        ),
                    ]
                ]
            ),
        )
