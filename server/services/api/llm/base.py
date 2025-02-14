"""The module responsible for the basic interface of interaction with LLM."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Literal


@dataclass
class Prompt(object):
    """Class representing the industrial structure."""

    role: Literal["user", "system", "assistant"]
    text: str

    def to_dict(self) -> Dict[str, str]:
        """Return dict with fields from class."""
        return {"role": self.role, "text": self.text}


class BaseLLMAPI(ABC):
    """The basic interface for working with LLM."""

    @abstractmethod
    def send_prompts(self, chat: List[Prompt]) -> List[Prompt]:
        """Send messages to LLM."""
        pass
