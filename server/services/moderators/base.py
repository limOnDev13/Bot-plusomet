from abc import ABC, abstractmethod

from schemas.messages import MessageSchema, ModerationResultSchema


class BaseModerator(ABC):

    @abstractmethod
    def moderate(self, msg: MessageSchema) -> ModerationResultSchema:
        pass
