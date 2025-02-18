"""The module responsible for testing the work with the Yandex GPT API."""

from typing import List

import pytest

from server.config.app_config import Config
from server.services.api.llm.yandex_gpt import YandexGPTAPI
from server.services.prompts import Prompt


def test_yandex_gpt_auth(config: Config):
    """Test authentication."""
    try:
        llm_api = YandexGPTAPI(config)
        llm_api.auth()
    except Exception as exc:
        pytest.fail(str(exc))


def test_send_simple_prompt(config: Config, simple_prompt: Prompt):
    """Test sending simple prompt."""
    try:
        llm_api = YandexGPTAPI(config)
        llm_api.auth()

        answers: List[Prompt] = llm_api.send_prompts([simple_prompt])
        for answer in answers:
            print(answer.text)
    except Exception as exc:
        pytest.fail(str(exc))
