"""Conftest with fixtures for tests."""

import random
from typing import List

import pytest
from dotenv import load_dotenv

from server.config.app_config import Config, get_config
from server.schemas.messages import MessageSchema
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
def user_msgs() -> List[MessageSchema]:
    """Get list of examples of user messages."""
    return [
        MessageSchema(id=str(random.randint(0, 1000)), text="Привет, как дела?"),
        MessageSchema(id=str(random.randint(0, 1000)), text="Погода сегодня ясная"),
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Меня зовут Петя, я точно не нейронная сеть)))",
        ),
    ]


@pytest.fixture(scope="function")
def llm_generated_msgs() -> List[MessageSchema]:
    """Get list of examples of generated msgs by LLM."""
    return [
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Если вы хотите достичь успеха, вам нужно следовать этим шагам: "
            "1) Поставьте цель. 2) Разработайте план. 3) Действуйте. "
            "4) Анализируйте результаты. 5) Повторяйте процесс до достижения успеха.",
        ),
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Здравствуйте! Благодарю вас за ваше обращение. "
            "Пожалуйста, уточните, чем я могу быть вам полезен сегодня? "
            "Буду рад помочь вам в решении вашего вопроса.",
        ),
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Вот три причины, почему это решение подходит вам: "
            "1) Оно экономит время. 2) Оно повышает эффективность. "
            "3) Оно снижает затраты. Таким образом,"
            " это решение является оптимальным.",
        ),
    ]


@pytest.fixture(scope="function")
def toxic_msgs() -> List[MessageSchema]:
    """Get list of examples of toxic messages."""
    return [
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Ты вообще тупой? Как можно не понимать таких элементарных вещей?",
        ),
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Ну конечно, ты как всегда всё знаешь лучше всех."
            " Ну давай, продолжай умничать.",
        ),
        MessageSchema(
            id=str(random.randint(0, 1000)),
            text="Я такого не говорил. Ты точно всё правильно понял? Может, "
            "у тебя с памятью проблемы?",
        ),
    ]
