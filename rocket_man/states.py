import random

from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.engine import BaseState
from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr

from rocket_man.services import FrameXService
from rocket_man.utils import url_to_markdown


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
        print("Error!")
        self.send(lyr.Text(t.ERROR))

    @page_view("/bot/confused")
    async def confused(self) -> None:
        """
        This is called when the user sends a message that triggers no
        transitions.
        """
        print("Confused!")
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
            lyr.Text("I'd like to show you pictures of a rocket launch and ask you if it has launched yet."),
            lyr.Text("What do you say?"),
            has_launched_or_good_bye(),
        )


def has_launched_or_good_bye():
    return tgr.InlineKeyboard(
        [
            [
                tgr.InlineKeyboardCallbackButton(
                    text="YAY",
                    payload={"action": "has_launched", "step": 1},
                ),
                tgr.InlineKeyboardCallbackButton(
                    text="NAY",
                    payload={"action": "good_bye"},
                ),
            ]
        ]
    )


class HasLaunched(RocketManState):
    """
    Example state that shows an image and a keyboard.
    """

    @page_view("/bot/has_launched")
    async def handle(self) -> None:
        print("Has Launched?")

        step = 1
        if self.request.has_layer(lyr.Postback):
            payload = self.request.get_layer(lyr.Postback).payload
            print("Postback", payload)
            step = payload.get("step")
            if isinstance(step, int) and step > 1:
                lo = payload.get("lo")
                hi = payload.get("hi")
                mid = payload.get("mid")
                cond = payload.get("cond")
                video_name = payload.get("video_name")
                if lo is None or hi is None or cond is None or video_name is None:
                    step = 1
        if step == 1:
            # choose a random image
            async with FrameXService() as fx:
                videos = await fx.list_videos()
                vid = random.choice(videos)
                lo, hi = 0, vid.frames
                video_name = vid.name
                cond = None
        else:
            if cond == "ge":
                hi = mid
            else:
                lo = mid + 1

        step += 1
        if lo == hi:
            self.send(
                lyr.Text("Thanks!"),
                lyr.Text("You helped me find the right frame in {step} steps!"),
                lyr.Text("Wanna try again?"),
                has_launched_or_good_bye(),
            )
            return

        mid = (lo + hi) // 2
        frame_url = FrameXService.get_video_frame_url(video_name, mid)

        self.send(
            lyr.Markdown(f"Has [the rocket]({url_to_markdown(frame_url)}) launched yet?"),
            tgr.InlineKeyboard(
                [
                    [
                        tgr.InlineKeyboardCallbackButton(
                            text="YES",
                            payload=dict(
                                action="has_launched",
                                lo=lo,
                                hi=hi,
                                mid=mid,
                                cond="ge",
                                step=step,
                                video_name=video_name,
                            ),
                        ),
                        tgr.InlineKeyboardCallbackButton(
                            text="NO",
                            payload=dict(
                                action="has_launched",
                                lo=lo,
                                hi=hi,
                                mid=mid,
                                cond="lt",
                                step=step,
                                video_name=video_name,
                            ),
                        ),
                    ]
                ]
            ),
        )
