from bernard.engine import Tr
from bernard.engine import triggers as trg
from bernard.i18n import intents as its

from .states import HasLaunched, Hello

transitions = [
    Tr(
        dest=Hello,
        factory=trg.Text.builder(its.HELLO),
    ),
    Tr(dest=HasLaunched, origin=Hello, factory=trg.Action.builder("has_launched")),
    Tr(dest=HasLaunched, origin=HasLaunched, factory=trg.Action.builder("has_launched")),
]
