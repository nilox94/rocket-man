from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.i18n import translate as t

from rocket_man.states.base import RocketManState
from rocket_man.states.common import has_launched_or_goodbye


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
