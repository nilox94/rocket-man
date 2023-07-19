import logging

import ujson
from aiohttp.web_request import Request
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

    async def call(self, method: str, _ignore: set[str] | None = None, **params: dict):
        """
        Call a telegram method

        :param _ignore: List of reasons to ignore
        :param method: Name of the method to call
        :param params: Dictionary of the parameters to send

        :return: Returns the API response
        """
        try:
            return await super().call(method, _ignore, **params)
        except Exception as err:
            logger.exception("Telegram API call failed")
            await self.send_failure(params["chat_id"])
            raise err

    async def send_failure(self, chat_id: int):
        """
        Sends a failure message to the user
        """
        method = "sendMessage"
        params = {
            "chat_id": chat_id,
            "text": "You broke the bot!\nNice job :D\nTry again later.",
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
