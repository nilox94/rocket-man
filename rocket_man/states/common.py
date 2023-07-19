from bernard.i18n import translate as t
from bernard.platforms.telegram import layers as tgr


def has_launched_or_goodbye():
    return tgr.InlineKeyboard(
        [
            [
                tgr.InlineKeyboardCallbackButton(
                    text=t.YES,
                    payload={"action": "has_launched"},
                ),
                tgr.InlineKeyboardCallbackButton(
                    text=t.NO,
                    payload={"action": "goodbye"},
                ),
            ]
        ]
    )
