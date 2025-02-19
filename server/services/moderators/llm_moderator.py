"""The module responsible for moderation through LLM."""

import json
import random
import time
from dataclasses import asdict
from json.decoder import JSONDecodeError
from logging import getLogger
from typing import Any, Dict, List

from schemas.messages import MessageSchema, ModerationResultSchema
from server.config.app_config import ModerationConfig
from server.services.api.llm.base import BaseLLMAPI
from server.services.excs import (
    APIAuthException,
    IncorrectEncodingError,
    IncorrectFormatError,
    PromptError,
    TooManyRequests,
)
from server.services.prompts import PROMPTS, Prompt

from .base import BaseModerator

logger = getLogger("main.services.moderator")


class LLMModerator(BaseModerator):
    """The class responsible for moderation of messages using LLM."""

    def __init__(self, llm_api: BaseLLMAPI, config: ModerationConfig):
        """
        Init class.

        :param llm_api: BaseLLMAPI object.
        :param config: Config for moderation.
        """
        self.__llm_api = llm_api
        self.__delay_limits = config.random_delay_limits
        self.__default_delay: float = self.__update_default_delay()
        self.__delay = self.__default_delay
        self.__max_num_retries = config.max_num_retries
        self.__delay_dominator = config.delay_denominator

        self.__retries: int = 0

    def __update_default_delay(self) -> float:
        return random.uniform(*self.__delay_limits)

    @classmethod
    def __process_llm_answer(
        cls, prompts: List[Prompt], answer: Prompt, message: MessageSchema
    ) -> Dict[str, Any]:
        """Decode answer from LLM."""
        answer_json_str: str = answer.text.strip("```").strip()

        try:
            processed_answer: Dict[str, Any] = json.loads(answer_json_str)
            processed_answer["msg_id"] = message.id
            return processed_answer
        except JSONDecodeError:
            raise IncorrectEncodingError(
                prompts=prompts,
                answer=answer,
                msg="LLM returned an answer that cannot be decoded from JSON.",
            )

    def __moderation_process(self, message: MessageSchema) -> ModerationResultSchema:
        """
        Moderate msg.

        :param message: User message.
        :return: ModerationResult
        :raise PromptError: If LLM returned more than 1 answer.
        :raise IncorrectEncodingError: If LLM returned an answer
        that cannot be decoded from JSON.
        :raise IncorrectFormatError: If LLM returned an answer
        that cannot be converted to a ModerationResult
        """
        prompts: List[Prompt] = [
            PROMPTS["moderation_prompt"],
            Prompt(role="user", text=message.text),
        ]
        answers: List[Prompt] = self.__llm_api.send_prompts(prompts)

        if len(answers) != 1:
            raise PromptError(msg="LLM returned more than 1 answer.", prompts=prompts)
        processed_answer: Dict[str, Any] = self.__process_llm_answer(
            prompts, answers[0], message
        )

        try:
            return ModerationResultSchema(**processed_answer)
        except TypeError:
            raise IncorrectFormatError(
                prompts=prompts,
                msg="LLM returned an answer in the wrong format",
                expected=json.dumps(
                    asdict(ModerationResultSchema("1", True, True)), indent=4
                ),
                received=json.dumps(processed_answer, indent=4),
            )

    def __sleep(self, retry_backoff: bool = False) -> None:
        """
        Make a delay.

        :param retry_backoff: If True, the delay will
        increase by a factor of self.__delay_dominator.
        :return: None
        """
        self.__retries += 1
        if retry_backoff:
            time.sleep(self.__delay)
            self.__delay *= self.__delay_dominator
        else:
            time.sleep(self.__default_delay)

    def moderate(self, message: MessageSchema) -> ModerationResultSchema:
        """
        Moderate msg.

        The function is trying to moderate the message.
        If APIAuthException and TooManyRequests occur during operation,
        the function delays and tries to moderate the message again.
        If an APIAuthException occurs, the function makes a standard delay,
        tries to authenticate and make the request again.
        If a TooManyRequests exception occurs, the function makes an exponential
        delay and repeats the request again. The number of attempts is limited.
        If other exceptions occur or the attempt limit is exceeded,
        the exception is thrown further.

        :param message: User message.
        :return: Result of moderation.
        """
        try:
            result: ModerationResultSchema = self.__moderation_process(message)
            self.__sleep()
        except APIAuthException as exc:
            logger.warning(
                "Authorization error on the %s service." " Trying to auth again...",
                exc.service_name,
            )
            if self.__retries >= self.__max_num_retries:
                raise

            # delay
            self.__sleep()
            # re-auth
            self.__llm_api.auth()
            # moderate again
            return self.moderate(message)
        except TooManyRequests as exc:
            logger.warning(
                "There are too many requests to the %s service."
                " Trying to make a request again...",
                exc.service_name,
            )
            if self.__retries >= self.__max_num_retries:
                raise

            # exponential delay
            self.__sleep(retry_backoff=True)
            # moderate again
            return self.moderate(message)
        else:
            return result
        finally:
            self.__retries = 0
            self.__default_delay = self.__update_default_delay()
            self.__delay = self.__default_delay
