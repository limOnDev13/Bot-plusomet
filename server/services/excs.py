"""The module responsible for custom exceptions."""

import json
from dataclasses import asdict
from typing import Any, List, Optional

from server.services.prompts import Prompt


class APIException(Exception):
    """The exception is for errors from third-party APIs."""

    def __init__(
        self,
        service_name: str,
        status_code: int,
        msg: Optional[str] = None,
        json_str: Optional[str] = None,
    ):
        """
        Init class.

        :param service_name: Name of API service.
        :param status_code: Status code.
        :param msg: Message from server.
        :param json_str: JSON from server.
        """
        self.service_name = service_name
        self.msg = msg
        self.json_str = json_str
        self.status_code = status_code

    def __str__(self) -> str:
        """Return str of exception."""
        res_str: str = (
            f"Service: {self.service_name}\nStatus code: {self.status_code}\n"
        )
        if self.msg:
            res_str += ", ".join((res_str, self.msg))
        if self.json_str:
            res_str += ", ".join((res_str, json.dumps(self.json_str, indent=2)))

        return res_str


class APIAuthException(APIException):
    """The exception is for errors related to auth on third-party APIs."""

    def __init__(
        self,
        service_name: str,
        status_code: int = 401,
        msg: Optional[str] = None,
        json_str: Optional[str] = None,
    ):
        """
        Init class.

        :param service_name: Name of API service.
        :param status_code: Status code.
        :param msg: Message from server.
        :param json_str: JSON from server.
        """
        super().__init__(service_name, status_code, msg, json_str)


class TooManyRequests(APIException):
    """Exception responsible for code error 429 (Too Many Requests)."""

    def __init__(
        self,
        service_name: str,
        status_code: int = 429,
        msg: Optional[str] = None,
        json_str: Optional[str] = None,
    ):
        """
        Init class.

        :param service_name: Name of API service.
        :param status_code: Status code.
        :param msg: Message from server.
        :param json_str: JSON from server.
        """
        super().__init__(service_name, status_code, msg, json_str)


class PromptError(Exception):
    """The exception is for errors related to incorrect prompt logic."""

    def __init__(self, prompts: List[Prompt], msg: Optional[str] = None):
        """
        Init exception.

        :param prompts: Chat history.
        :param msg: Exception message.
        """
        self.prompts = prompts
        self.msg = msg

    def __str__(self) -> str:
        """Return str of exception."""
        return (
            f"{self.msg}\n"
            f"Chat history:\n"
            f"{json.dumps([asdict(prompt) for prompt in self.prompts], indent=2)}"
        )


class IncorrectEncodingError(PromptError):
    """The exc responsible for errors related to invalid encoding of the LLM answer."""

    def __init__(
        self, prompts: List[Prompt], answer: Prompt, msg: Optional[str] = None
    ):
        """
        Init class.

        :param prompts: Chat history.
        :param answer: LLM answer.
        :param msg: Exception message.
        """
        super().__init__(prompts, msg)
        self.answer = answer

    def __str__(self) -> str:
        """Return str of exception."""
        exc_text: str = super().__str__()
        return "\n".join((exc_text, f"Answer:\n{self.answer.text}"))


class IncorrectFormatError(PromptError):
    """The exc responsible for errors related to the invalid answer format from LLM."""

    def __init__(
        self,
        prompts: List[Prompt],
        msg: Optional[str] = None,
        expected: Any = None,
        received: Any = None,
    ):
        """
        Init exception.

        :param prompts: Chat history.
        :param msg: Message.
        :param expected: Expected format of example of correct answer.
        :param received: Received answer.
        """
        super().__init__(prompts=prompts, msg=msg)
        self.expected = expected
        self.received = received

    def __str__(self) -> str:
        """Return str of exception."""
        res_str: str = super().__str__()
        if self.expected is not None:
            return "\n".join(
                (res_str, f"Expected:\n{self.expected}\nReceived:\n{self.received}")
            )
        return res_str
