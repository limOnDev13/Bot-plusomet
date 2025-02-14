"""The module responsible for getting the configuration from the env variables."""

import os
from dataclasses import dataclass


@dataclass
class Config(object):
    """Config class for the app."""

    debug: bool


def get_config() -> Config:
    """Return app config."""
    return Config(
        debug=os.getenv("SERVER_DEBUG", "0") == "1",
    )
