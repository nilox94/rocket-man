from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.i18n import translate as t

from rocket_man.states.base import RocketManState


class Goodbye(RocketManState):
    @page_view("/bot/goodbye")
    async def handle(self):
        self.send(lyr.Text(t.GOODBYE))
