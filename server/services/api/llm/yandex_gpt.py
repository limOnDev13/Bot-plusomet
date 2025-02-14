"""The module responsible for working with the YandexGPT API."""

from typing import Any, Dict, List

import requests
from requests import Response

from server.config.app_config import Config

from .base import BaseLLMAPI, Prompt


class YandexGPTAPI(BaseLLMAPI):
    """A class for working with YandexGPT."""

    def __init__(self, config: Config):
        """
        Init class.

        :param config: app config.
        """
        self.__iam_token = config.yandex_gpt.iam_token
        self.__catalog_id = config.yandex_gpt.catalog_id
        self.__temperature = config.yandex_gpt.temperature
        self.__max_tokens = config.yandex_gpt.max_tokens

        self.__url: str = (
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        )
        self.__headers: Dict[str, Any] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__iam_token}",
            "x-data-logging-enabled": False,
        }
        self.__data: Dict[str, Any] = {
            "modelUri": f"gpt://{self.__catalog_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": self.__temperature,
                "maxTokens": self.__max_tokens,
                "reasoningOptions": {"mode": "DISABLED"},
            },
        }

    def send_prompts(self, chat: List[Prompt]) -> List[Prompt]:
        """
        Send prompts to YandexGPT.

        :param chat: Messages history.
        :return: A list of responses from YandexGPT in the form of prompts.
        """
        self.__data["messages"] = [prompt.to_dict() for prompt in chat]

        response: Response = requests.get(
            self.__url,
            headers=self.__headers,
            json=self.__data,
        )

        llm_answers: List[Dict[str, Any]] = response.json()["result"]["alternatives"]
        return [Prompt(**llm_answer["message"]) for llm_answer in llm_answers]
