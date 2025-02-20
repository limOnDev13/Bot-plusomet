"""The module responsible for the interfaces Producer/Consumer messages."""

from abc import ABC, abstractmethod

from schemas.messages import MessageSchema


class BaseMessageProducer(ABC):
    """Base message Producer interface."""

    @abstractmethod
    async def upload(self, msg: MessageSchema) -> None:
        """Upload message."""
        pass


class BaseMessageConsumer(ABC):
    """Base message Consumer interface."""

    @abstractmethod
    async def extract(self) -> MessageSchema:
        """Extract message."""
        pass
