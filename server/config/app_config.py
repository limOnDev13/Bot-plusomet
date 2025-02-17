"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass
from typing import List


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
    yandex_gpt: YandexGPTConfig
    celery: CeleryConfig


def get_config() -> Config:
    """Return app config."""
    return Config(
        debug=os.getenv("SERVER_DEBUG", "0") == "1",
        yandex_gpt=YandexGPTConfig(
            oauth_token=os.getenv("YANDEXGPT_OAUTH", ""),
            catalog_id=os.getenv("YANDEXGPT_CATALOG_ID", ""),
            temperature=float(os.getenv("YANDEXGPT_TEMPERATURE", 0.3)),
            max_tokens=int(os.getenv("YANDEXGPT_MAX_TOKENS", 2000)),
        ),
        celery=CeleryConfig(
            broker_url=os.getenv("CELERY_BROKER"),
            result_backed=os.getenv("CELERY_BACKEND"),
            accept_content=os.getenv("CELERY_ACCEPT_CONTENT").split(","),
            result_expires=int(os.getenv("CELERY_RESULT_EXPIRES"), 3600),
        ),
    )
