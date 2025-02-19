"""The module responsible for the interface of all moderators."""

from abc import ABC, abstractmethod

from schemas.messages import MessageSchema, ModerationResultSchema


class BaseModerator(ABC):
    """The moderator's basic interface."""

    @abstractmethod
    def moderate(self, msg: MessageSchema) -> ModerationResultSchema:
        """Moderate msg."""
        pass
