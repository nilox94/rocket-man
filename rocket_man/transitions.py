from bernard.engine import Tr
from bernard.engine.triggers import Action, Text
from bernard.i18n import intents as its

from rocket_man.states import Goodbye, HasLaunched, Hello, MaybeHasLaunched
from rocket_man.triggers import HasLaunchedTrigger, MaybeHasLaunchedTrigger

transitions = [
    Tr(dest=Hello, factory=Text.builder(its.HELLO)),
    Tr(dest=HasLaunched, origin=Hello, factory=Action.builder("has_launched")),
    Tr(dest=HasLaunched, origin=HasLaunched, factory=HasLaunchedTrigger),
    Tr(dest=MaybeHasLaunched, origin=HasLaunched, factory=MaybeHasLaunchedTrigger),
    Tr(dest=Goodbye, factory=Action.builder("goodbye")),
]
