from logging import getLogger
from pathlib import Path
from typing import Any

from pydantic import HttpUrl, RedisDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger(__name__)


project_root = Path(__file__).parent.parent
i18n_root = project_root / "i18n"


# --- Environment variables ---


class Settings(BaseSettings):
    """
    This class contains all the settings for the bot.
    You can override them using environment variables or a `.env` file.
    """

    model_config = SettingsConfigDict(
        env_file=project_root / ".env",
        env_file_encoding="utf-8",
    )

    debug: bool = False
    code_live_reload: bool = False  # for now, only supported on Linux & Python < 3.11

    bernard_base_url: HttpUrl | None = None

    webview_secret_key: str = ""
    sentry_dsn: str = ""

    socket_path: Path | None = None
    bind_host: str = "127.0.0.1"
    bind_port: int = 8080

    redis_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore[assignment]

    fb_page_token: str = ""
    fb_app_id: str = ""
    fb_app_secret: str = ""
    fb_page_id: str = ""

    telegram_token: str = ""

    @field_validator("fb_app_id", "fb_app_secret", "fb_page_id")
    def check_fb_settings(cls, v: str, info: FieldValidationInfo):
        """ "
        Check that all Facebook settings are set if FB_PAGE_TOKEN is set
        """
        if info.data["fb_page_token"] and not v:
            raise ValueError("Facebook settings are not set")
        return v


env = Settings()


def make_whitelist():
    """
    Generates the list of whitelisted domains for webviews. This is especially
    useful when you create your Facebook Messenger configuration.

    Don't hesitate to change this function to add more domains if you need it.
    """

    origin = str(env.bernard_base_url.origin())
    if origin:
        return [origin]
    return []


DEBUG = env.debug

if DEBUG:
    import stackprinter

    stackprinter.set_excepthook(style="darkbg2")

CODE_LIVE_RELOAD = env.code_live_reload

SENTRY_DSN = env.sentry_dsn
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            AioHttpIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )

# --- Starting points ---

# This module contains the transitions and is loaded to generate the FSM.
TRANSITIONS_MODULE = "rocket_man.transitions"

# The default state is used whenever something goes wrong which prevents a
# state to be chosen. In this case, it will ball back to the default state
# in order to produce an error message. This default state must also be the
# common ancestor of all your states in order for them to inherit the default
# error messages.
DEFAULT_STATE = "rocket_man.states.RocketManState"

# --- Platforms ---

# That's the configuration tokens for all the platforms you want to manage.
PLATFORMS = []

# Adds the Facebook support if Facebook tokens are detected. Don't forget
# to set everything right in the Facebook developers website
# https://developers.facebook.com/
if env.fb_page_token:
    PLATFORMS.append(
        {
            "class": "bernard.platforms.facebook.platform.Facebook",
            "settings": {
                "app_id": env.fb_app_id,
                "app_secret": env.fb_app_secret,
                "page_id": env.fb_page_id,
                "page_token": env.fb_page_token,
            },
            # https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/greeting
            "greeting": [
                {
                    "locale": "default",
                    "text": "Welcome to this BERNARD bot!",
                }
            ],
            # https://developers.facebook.com/docs/messenger-platform/send-messages/persistent-menu
            "menu": [
                {
                    "locale": "default",
                    "call_to_actions": [
                        {
                            "title": "Get started again",
                            "type": "postback",
                            "payload": '{"action": "get_started"}',
                        },
                    ],
                }
            ],
            # https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/domain-whitelisting
            "whitelist": make_whitelist(),
        }
    )

# Adds Telegram support if Telegram tokens are detected. Don't forget to
# register and configure your bot by talking to @BotFather
if env.telegram_token:
    PLATFORMS.append(
        {
            "class": "rocket_man.platforms.RocketTg",
            "settings": {
                "token": env.telegram_token,
            },
        }
    )

# --- Self-awareness ---

# Public base URL, used to generate links to the bot itself.
BERNARD_BASE_URL = str(env.bernard_base_url) if env.bernard_base_url else None

# Secret key that serves in particular to sign content sent to the webview, but
# also in other places where signed content is required (aka when something
# goes outside and back again).
WEBVIEW_SECRET_KEY = env.webview_secret_key

# --- Network configuration ---

# That's a way to configure the network binding. If you define the SOCKET_PATH
# environment variable, then it will bind to the specified path as a UNIX
# socket. Otherwise it will look at BIND_PORT to know which TCP port to bind to
# and will fall back to 8666.

if env.socket_path:
    SERVER_BIND: dict[str, Any] = {
        "path": env.socket_path,
    }
else:
    SERVER_BIND = {
        "host": env.bind_host,
        "port": env.bind_port,
    }

# By default, store the register in local redis
REGISTER_STORE = {
    "class": "bernard.storage.register.RedisRegisterStore",
    "params": {
        "host": env.redis_url.host,
        "port": env.redis_url.port,
        "db_id": int((env.redis_url.path)[1:]),  # type: ignore[index]
    },
}

# --- Natural language understanding/generation ---

# List of intents loaders, typically CSV files with intents.
I18N_INTENTS_LOADERS = [
    {
        "loader": "bernard.i18n.loaders.CsvIntentsLoader",
        "params": {
            "file_path": i18n_root / "en" / "intents.csv",
            "locale": "en",
        },
    },
]

# List of translation loaders, typically CSV files with translations.
I18N_TRANSLATION_LOADERS = [
    {
        "loader": "bernard.i18n.loaders.CsvTranslationLoader",
        "params": {
            "file_path": i18n_root / "en" / "responses.csv",
            "locale": "en",
        },
    },
]

# --- Middlewares ---

# All your middlewares. The default ones are here to slow down the sending of
# messages and make it look more natural.
MIDDLEWARES = [
    # "bernard.middleware.AutoSleep",
    "bernard.middleware.AutoType",
]

# Sleeping offset before any message
USERS_READING_BUBBLE_START = 0.0

# How many words per minute can your users read? This will compute the delay
# for each message automatically.
USERS_READING_SPEED = 200
