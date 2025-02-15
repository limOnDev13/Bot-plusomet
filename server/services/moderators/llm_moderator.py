"""The module responsible for moderation through LLM."""

import json
from dataclasses import dataclass
from json import JSONDecodeError
from logging import getLogger
from typing import Dict, List

from server.services.api.llm.base import BaseLLMAPI
from server.services.excs import (
    IncorrectEncodingError,
    IncorrectFormatError,
    PromptError,
)
from server.services.prompts import PROMPTS, Prompt

logger = getLogger("main.services.moderator")


@dataclass
class ModerationResult(object):
    """The structure of the LLM response after message moderation."""

    generated_by_llm: bool
    toxic: bool

    def to_dict(self) -> Dict[str, bool]:
        """Return the object representation as a dictionary."""
        return {"generated_by_llm": self.generated_by_llm, "toxic": self.toxic}


class LLMModerator(object):
    """The class responsible for moderation of messages using LLM."""

    def __init__(self, llm_api: BaseLLMAPI):
        self.__llm_api = llm_api

    def moderate(self, message: str) -> ModerationResult:
        """
        Moderate msg.

        :param message: User message.
        :return: ModerationResult
        :raise PromptError: If LLM returned more than 1 answer.
        :raise IncorrectEncodingError: If LLM returned an answer that cannot be decoded from JSON.
        :raise IncorrectFormatError: If LLM returned an answer that cannot be converted to a ModerationResult
        """
        prompts: List[Prompt] = [
            PROMPTS["moderation_prompt"],
            Prompt(role="user", text=message),
        ]
        answers: List[Prompt] = self.__llm_api.send_prompts(prompts)

        if len(answers) != 1:
            raise PromptError(msg="LLM returned more than 1 answer.", prompts=prompts)
        answer = answers[0].text.strip("```").strip()

        try:
            return ModerationResult(**json.loads(answer))
        except JSONDecodeError:
            raise IncorrectEncodingError(
                msg="LLM returned an answer that cannot be decoded from JSON.",
                prompts=prompts,
            )
        except TypeError:
            raise IncorrectFormatError(
                msg="LLM returned an answer in the wrong format",
                prompts=prompts,
                expected=json.dumps(ModerationResult(True, True).to_dict(), indent=2),
                received=json.dumps(json.loads(answer), indent=2),
            )
