"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class YandexGPTConfig(object):
    """Config for work with YandexGPT API."""

    oauth_token: str
    catalog_id: str
    temperature: float
    max_tokens: int


@dataclass
class CeleryConfig(object):
    """Config for Celery."""

    broker_url: str
    result_backed: str
    accept_content: List[str]
    result_expires: int


@dataclass
class Config(object):
    """Config class for the app."""

    debug: bool
    moderation_random_delay: Tuple[float, float]
    yandex_gpt: YandexGPTConfig
    celery: CeleryConfig


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
        or float(moderation_max_delay_str) < moderation_min_delay
    ):
        moderation_max_delay = moderation_min_delay
    else:
        moderation_max_delay = float(moderation_max_delay_str)

    return moderation_min_delay, moderation_max_delay


def get_config() -> Config:
    """Return app config."""
    return Config(
        debug=os.getenv("SERVER_DEBUG", "0") == "1",
        moderation_random_delay=__moderation_random_delay(),
        yandex_gpt=YandexGPTConfig(
            oauth_token=os.getenv("YANDEXGPT_OAUTH", ""),
            catalog_id=os.getenv("YANDEXGPT_CATALOG_ID", ""),
            temperature=float(os.getenv("YANDEXGPT_TEMPERATURE", 0.3)),
            max_tokens=int(os.getenv("YANDEXGPT_MAX_TOKENS", 2000)),
        ),
        celery=CeleryConfig(
            broker_url=os.getenv("CELERY_BROKER", "redis://localhost:6379/0"),
            result_backed=os.getenv("CELERY_BACKEND", "redis://localhost:6379/0"),
            accept_content=os.getenv("CELERY_ACCEPT_CONTENT", "json,").split(","),
            result_expires=int(os.getenv("CELERY_RESULT_EXPIRES", 3600)),
        ),
    )
