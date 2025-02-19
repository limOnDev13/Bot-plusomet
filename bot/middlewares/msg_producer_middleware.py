"""Module responsible with middlewares for forwarding msg_producer inside handlers."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from producer_consumer.messages.redis_pc import RedisMessageProducer


class MsgProducerMiddleware(BaseMiddleware):
    """Middleware for forwarding msg_producer inside handlers."""

    def __init__(self, msg_producer: RedisMessageProducer):
        """
        Init class.

        :param msg_producer: Message Producer.
        """
        self.__msg_producer = msg_producer

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Forward msg_producer inside handler."""
        data["msg_producer"] = self.__msg_producer
        return await handler(event, data)
