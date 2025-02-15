"""The module responsible for the basic interface of interaction with LLM."""

from abc import ABC, abstractmethod
from typing import List

from server.services.prompts import Prompt


class BaseLLMAPI(ABC):
    """The basic interface for working with LLM."""

    @abstractmethod
    def send_prompts(self, chat: List[Prompt]) -> List[Prompt]:
        """Send messages to LLM."""
        pass
