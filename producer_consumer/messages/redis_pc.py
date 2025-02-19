"""The module responsible for implementing the Redis-based moderation results P/C."""

import json
from dataclasses import asdict

import redis

from schemas.messages import MessageSchema

from .base import BaseMessageConsumer, BaseMessageProducer


class RedisMessageConsumer(BaseMessageConsumer):
    """Redis-based message Consumer."""

    def __init__(self, redis_client: redis.asyncio.Redis, queue_name: str = "messages"):
        """
        Init class.

        :param redis_client: Redis client.
        :param queue_name: The names of the queue in which the messages will be stored.
        """
        self.__client = redis_client
        self.__queue_name = queue_name

    async def extract(self) -> MessageSchema:
        """Extract the message from the repository."""
        _, msg = await self.__client.blpop([self.__queue_name], timeout=None)
        return MessageSchema(**json.loads(msg))


class RedisMessageProducer(BaseMessageProducer):
    """Redis-based message Producer."""

    def __init__(self, redis_client: redis.asyncio.Redis, queue_name: str = "messages"):
        """
        Init class.

        :param redis_client: Redis client.
        :param queue_name: The names of the queue in which the messages will be stored.
        """
        self.__client = redis_client
        self.__queue_name = queue_name

    async def upload(self, msg: MessageSchema) -> None:
        """Upload message."""
        await self.__client.rpush(self.__queue_name, json.dumps(asdict(msg)))
