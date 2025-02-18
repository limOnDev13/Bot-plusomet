"""The module responsible for moderation through LLM."""

import json
import random
import time
from dataclasses import asdict
from json.decoder import JSONDecodeError
from logging import getLogger
from typing import Any, Dict, List, Tuple

from server.schemas.messages import MessageSchema, ModerationResultSchema
from server.services.api.llm.base import BaseLLMAPI
from server.services.excs import (
    IncorrectEncodingError,
    IncorrectFormatError,
    PromptError,
)
from server.services.prompts import PROMPTS, Prompt

logger = getLogger("main.services.moderator")


class LLMModerator(object):
    """The class responsible for moderation of messages using LLM."""

    def __init__(self, llm_api: BaseLLMAPI, random_delay: Tuple[float, float] = (1, 3)):
        """
        Init class.

        :param llm_api: BaseLLMAPI object.
        :param random_delay: The boundaries of the random delay value.
        :raise ValueError: If random_delay[0] > random_delay[1]
        """
        self.llm_api = llm_api

        if random_delay[0] > random_delay[1]:
            raise ValueError(f"{random_delay[0]=} must be no more {random_delay[1]=}")
        self.__random_delay = random_delay

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

    def moderate(self, message: MessageSchema) -> ModerationResultSchema:
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
        answers: List[Prompt] = self.llm_api.send_prompts(prompts)

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
        finally:
            time.sleep(random.uniform(*self.__random_delay))
