from bernard.engine import Tr
from bernard.engine import triggers as trg
from bernard.i18n import intents as its

from rocket_man.states import Goodbye, HasLaunched, Hello, MaybeHasLaunched
from rocket_man.triggers import HasLaunchedTrigger, MaybeHasLaunchedTrigger

transitions = [
    Tr(dest=Hello, factory=trg.Text.builder(its.HELLO)),
    Tr(dest=HasLaunched, origin=Hello, factory=trg.Action.builder(action="has_launched")),
    Tr(dest=HasLaunched, origin=HasLaunched, factory=HasLaunchedTrigger.builder(action="has_launched")),
    Tr(dest=MaybeHasLaunched, origin=HasLaunched, factory=MaybeHasLaunchedTrigger.builder(action="has_launched")),
    Tr(dest=Goodbye, factory=trg.Action.builder("goodbye")),
]
