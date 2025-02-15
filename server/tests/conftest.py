"""Conftest with fixtures for tests."""

from typing import List

import pytest
from dotenv import load_dotenv

from server.config.app_config import Config, get_config
from server.services.api.llm.base import BaseLLMAPI
from server.services.api.llm.yandex_gpt import YandexGPTAPI
from server.services.moderators.llm_moderator import LLMModerator


@pytest.fixture(scope="session")
def config() -> Config:
    """Get config from .env."""
    load_dotenv()
    return get_config()


@pytest.fixture(scope="session")
def llm_api(config: Config) -> BaseLLMAPI:
    """Get BaseLLMAPI object."""
    return YandexGPTAPI(config)


@pytest.fixture(scope="session")
def llm_moderator(llm_api: BaseLLMAPI) -> LLMModerator:
    """Get LLMModerator object."""
    return LLMModerator(llm_api)


@pytest.fixture(scope="function")
def user_msgs() -> List[str]:
    """Get list of examples of user messages."""
    return [
        "Привет, как дела?",
        "Погода сегодня ясная",
        "Меня зовут Петя, я точно не нейронная сеть)))",
    ]


@pytest.fixture(scope="function")
def llm_generated_msgs() -> List[str]:
    """Get list of examples of generated msgs by LLM."""
    return [
        "Если вы хотите достичь успеха, вам нужно следовать этим шагам: "
        "1) Поставьте цель. 2) Разработайте план. 3) Действуйте. "
        "4) Анализируйте результаты. 5) Повторяйте процесс до достижения успеха.",
        "Здравствуйте! Благодарю вас за ваше обращение. "
        "Пожалуйста, уточните, чем я могу быть вам полезен сегодня? "
        "Буду рад помочь вам в решении вашего вопроса.",
        "Вот три причины, почему это решение подходит вам: "
        "1) Оно экономит время. 2) Оно повышает эффективность. "
        "3) Оно снижает затраты. Таким образом,"
        " это решение является оптимальным.",
    ]


@pytest.fixture(scope="function")
def toxic_msgs() -> List[str]:
    """Get list of examples of toxic messages."""
    return [
        "Ты вообще тупой? Как можно не понимать таких элементарных вещей?",
        "Ну конечно, ты как всегда всё знаешь лучше всех."
        " Ну давай, продолжай умничать.",
        "Я такого не говорил. Ты точно всё правильно понял? Может, "
        "у тебя с памятью проблемы?",
    ]
