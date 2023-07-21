from typing import Generic

from bernard.storage.register import BaseRegisterStore

from rocket_man.storage.redis import Context, RedisMixin


class RegisterStore(RedisMixin, BaseRegisterStore, Generic[Context]):
    """
    Store the register in Redis.

    So far it is quite basic, especially regarding the locking mechanism which
    is just the bare minimum. This should seriously be improved in the future.
    """

    def __init__(self, content_prefix: str = "register::content:", lock_prefix: str = "register::lock:", **kwargs):
        super().__init__(content_prefix=content_prefix, lock_prefix=lock_prefix, **kwargs)
