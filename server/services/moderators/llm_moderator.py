"""The module responsible for moderation through LLM."""

import json
from dataclasses import asdict
from json import JSONDecodeError
from logging import getLogger
from typing import Any, Dict, List

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

    def __init__(self, llm_api: BaseLLMAPI):
        """
        Init class.

        :param llm_api: BaseLLMAPI object.
        """
        self.llm_api = llm_api

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
        answer = answers[0].text.strip("```").strip()
        answer_dict: Dict[str, Any] = dict()

        try:
            answer_dict = json.loads(answer)
            answer_dict["msg_id"] = message.id

            return ModerationResultSchema(**answer_dict)
        except JSONDecodeError:
            raise IncorrectEncodingError(
                msg="LLM returned an answer that cannot be decoded from JSON.",
                prompts=prompts,
            )
        except TypeError:
            raise IncorrectFormatError(
                msg="LLM returned an answer in the wrong format",
                prompts=prompts,
                expected=json.dumps(
                    asdict(
                        ModerationResultSchema(
                            msg_id=message.id,
                            generated_by_llm=True,
                            toxic=True,
                        )
                    ),
                    indent=2,
                ),
                received=json.dumps(answer_dict, indent=2),
            )
