"""The module responsible for the interfaces Producer/Consumer moderation results."""

from abc import ABC, abstractmethod

from schemas.messages import ModerationResultSchema


class BaseModerationResultProducer(ABC):
    """Base moderation results Producer interface."""

    @abstractmethod
    async def upload(self, mod_result: ModerationResultSchema) -> None:
        """Upload moderation result."""
        pass


class BaseModerationResultConsumer(ABC):
    """Base moderation results Consumer interface."""

    @abstractmethod
    async def extract(self) -> ModerationResultSchema:
        """Extract moderation result."""
        pass
