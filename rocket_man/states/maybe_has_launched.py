from bernard import layers as lyr
from bernard.analytics import page_view
from bernard.i18n import translate as t

from rocket_man.states.base import RocketManState
from rocket_man.states.common import has_launched_or_goodbye
from rocket_man.storage import context_store as cs


class MaybeHasLaunched(RocketManState):
    """ "
    The user wants to see a picture of the rocket launch,
    but we might have lost track of where they are in the process.
    e.g. context has expired.
    """

    @page_view("/bot/maybe_has_launched")
    @cs.inject()
    async def handle(self) -> None:
        self.send(
            lyr.Text(t.MAYBE_HAS_LAUNCHED),
            has_launched_or_goodbye(),
        )
