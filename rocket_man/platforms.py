from aiohttp.web_request import Request
from bernard.layers import Stack
from bernard.platforms.telegram.platform import Telegram


class RocketTg(Telegram):
    """
    BERNARD Telegram Platform with extended functionality
    """

    async def _send_markdown(self, request: Request, stack: Stack):
        """
        Sends Markdown using `_send_text()`
        """

        await self._send_text(request, stack, "MarkdownV2")
