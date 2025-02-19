"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass
class YandexGPTConfig(object):
    """Config for work with YandexGPT API."""

    oauth_token: str
    catalog_id: str
    temperature: float
    max_tokens: int


@dataclass
class ModerationConfig(object):
    """Config for moderation."""

    random_delay_limits: Tuple[float, float]
    delay_denominator: float
    max_num_retries: int


@dataclass
class Config(object):
    """Config class for the app."""

    debug: bool
    moderation_config: ModerationConfig
    yandex_gpt: YandexGPTConfig


def __moderation_random_delay() -> Tuple[float, float]:
    """Define the limits of random delay with foolproof protection."""
    moderation_min_delay_str = os.getenv("MODERATION_MIN_DELAY")
    moderation_max_delay_str = os.getenv("MODERATION_MAX_DELAY")

    if moderation_min_delay_str is None:
        moderation_min_delay = 1.0
    else:
        moderation_min_delay = abs(float(moderation_min_delay_str))

    if (
        moderation_max_delay_str is None
        or abs(float(moderation_max_delay_str)) < moderation_min_delay
    ):
        moderation_max_delay = moderation_min_delay
    else:
        moderation_max_delay = abs(float(moderation_max_delay_str))

    return moderation_min_delay, moderation_max_delay


def get_config() -> Config:
    """Return app config."""
    return Config(
        debug=os.getenv("SERVER_DEBUG", "0") == "1",
        moderation_config=ModerationConfig(
            random_delay_limits=__moderation_random_delay(),
            delay_denominator=max(1.0, float(os.getenv("DELAY_DENOMINATOR", 2))),
            max_num_retries=abs(int(os.getenv("MAX_NUM_RETRIES", 3))),
        ),
        yandex_gpt=YandexGPTConfig(
            oauth_token=os.getenv("YANDEXGPT_OAUTH", ""),
            catalog_id=os.getenv("YANDEXGPT_CATALOG_ID", ""),
            temperature=abs(float(os.getenv("YANDEXGPT_TEMPERATURE", 0.3))),
            max_tokens=abs(int(os.getenv("YANDEXGPT_MAX_TOKENS", 2000))),
        ),
    )
