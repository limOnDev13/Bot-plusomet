"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass


@dataclass
class YandexGPTConfig(object):
    """Config for work with YandexGPT API."""

    iam_token: str
    catalog_id: str
    temperature: float
    max_tokens: int


@dataclass
class Config(object):
    """Config class for the app."""

    debug: bool
    yandex_gpt: YandexGPTConfig


def get_config() -> Config:
    """Return app config."""
    return Config(
        debug=os.getenv("SERVER_DEBUG", "0") == "1",
        yandex_gpt=YandexGPTConfig(
            iam_token=os.getenv("YANDEXGPT_IAM", ""),
            catalog_id=os.getenv("YANDEXGPT_CATALOG_ID", ""),
            temperature=float(os.getenv("YANDEXGPT_TEMPERATURE", 0.3)),
            max_tokens=int(os.getenv("YANDEXGPT_MAX_TOKENS", 2000)),
        ),
    )
