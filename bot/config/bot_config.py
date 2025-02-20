"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass


@dataclass
class RedisConfig(object):
    """Config class for Redis."""

    url: str


@dataclass
class BotConfig(object):
    """Config class for bot."""

    debug: bool
    token: str
    chat_id: str
    is_premium: bool
    redis: RedisConfig


def get_config() -> BotConfig:
    """Return app config."""
    return BotConfig(
        debug=os.getenv("BOT_DEBUG", "1") == "1",
        token=os.getenv("BOT_TOKEN", ""),
        chat_id=os.getenv("BOT_CHAT_ID", ""),
        is_premium=os.getenv("BOT_IS_PREMIUM", "1") == "1",
        redis=RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost"),
        ),
    )
