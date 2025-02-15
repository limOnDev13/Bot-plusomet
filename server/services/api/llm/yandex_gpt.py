"""The module responsible for working with the YandexGPT API."""

from logging import getLogger
from typing import Any, Dict, List

import requests
from requests import Response

from server.config.app_config import Config
from server.services.excs import APIException

from .base import BaseLLMAPI, Prompt

logger = getLogger("main.api.YandexGPT")


class YandexGPTAPI(BaseLLMAPI):
    """A class for working with YandexGPT."""

    refresh_url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    base_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def __init__(self, config: Config):
        """
        Init class.

        :param config: app config.
        """
        self.__oauth_token = config.yandex_gpt.oauth_token
        self.__iam_token = config.yandex_gpt.iam_token
        self.__catalog_id = config.yandex_gpt.catalog_id
        self.__temperature = config.yandex_gpt.temperature
        self.__max_tokens = config.yandex_gpt.max_tokens

        self.__headers: Dict[str, Any] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__iam_token}",
            "x-data-logging-enabled": "false",
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

    def auth(self) -> None:
        """Get IAM token."""
        resp: Response = requests.post(
            self.refresh_url, data={"yandexPassportOauthToken": self.__oauth_token}
        )
        print(resp.json())

    def send_prompts(self, chat: List[Prompt]) -> List[Prompt]:
        """
        Send prompts to YandexGPT.

        :param chat: Messages history.
        :return: A list of responses from YandexGPT in the form of prompts.
        """
        self.__data["messages"] = [prompt.to_dict() for prompt in chat]
        logger.debug("Sending prompts")
        response: Response = requests.post(
            self.base_url,
            headers=self.__headers,
            json=self.__data,
        )
        if response.status_code != 200:
            raise APIException(
                service="YandexGPT",
                status_code=response.status_code,
                json_str=response.json(),
            )

        response_json = response.json()
        logger.debug(
            "LLM usage: inputTextTokens: %d, completionTokens: %d, totalTokens: %d",
            response_json["result"]["usage"]["inputTextTokens"],
            response_json["result"]["usage"]["completionTokens"],
            response_json["result"]["usage"]["totalTokens"],
        )

        llm_answers: List[Dict[str, Any]] = response_json["result"]["alternatives"]
        return [Prompt(**llm_answer["message"]) for llm_answer in llm_answers]
