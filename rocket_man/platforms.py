from asyncio import gather
from typing import Text

from aiohttp.web_request import Request
from bernard import layers as lyr
from bernard.engine.platform import PlatformOperationError
from bernard.i18n import render
from bernard.layers import Stack
from bernard.platforms.telegram.layers import Reply, Update
from bernard.platforms.telegram.platform import Telegram, set_reply_markup


class RocketTg(Telegram):
    """
    BERNARD Telegram Platform with extended functionality
    """

    async def _send_markdown(self, request: Request, stack: Stack):
        """
        Sends Markdown using `_send_text()`
        """

        await self._send_text(request, stack, "MarkdownV2")
