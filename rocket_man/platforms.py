import logging

import ujson
from aiohttp.web_request import Request
from bernard.i18n import render
from bernard.i18n import translate as t
from bernard.layers import Stack
from bernard.platforms.telegram.platform import Telegram

logger = logging.getLogger(__name__)


class RocketTg(Telegram):
    """
    BERNARD Telegram Platform with extended functionality
    """

    async def _send_markdown(self, request: Request, stack: Stack):
        """
        Sends Markdown using `_send_text()`
        """
        await self._send_text(request, stack, "MarkdownV2")

    async def send(self, request: Request, stack: Stack) -> None:
        """
        Send a stack to the platform.

        Actually this will delegate to one of the `_send_*` functions depending
        on what the stack looks like.
        """
        try:
            return await super().send(request, stack)
        except Exception as err:
            logger.exception("Error sending message to Telegram")
            await self.send_failure(request)
            raise err

    async def send_failure(self, request: Request):
        """
        Sends a failure message to the user
        """
        method = "sendMessage"
        params = {
            "chat_id": request.message.get_chat_id(),  # type: ignore[attr-defined]
            "text": await render(t.ERROR, request),
        }

        logger.debug("Calling Telegram %s(%s)", method, params)
        url = self.make_url(method)
        headers = {
            "content-type": "application/json",
        }

        async with self.session.post(
            url,
            data=ujson.dumps(params),
            headers=headers,
        ) as resp:
            data = await resp.json()
            logger.debug("Telegram replied: %s", data)
            return data
