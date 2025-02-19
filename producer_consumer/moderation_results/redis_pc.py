"""The module responsible for implementing the Redis-based P/C moderation results."""

import json
from dataclasses import asdict

import redis.asyncio

from schemas.messages import ModerationResultSchema

from .base import BaseModerationResultConsumer, BaseModerationResultProducer


class RedisModerationResultsConsumer(BaseModerationResultConsumer):
    """Redis-based moderation results Consumer."""

    def __init__(
        self, redis_client: redis.asyncio.Redis, queue_name: str = "moderation_results"
    ):
        """
        Init class.

        :param redis_client: Redis client.
        :param queue_name: The names of the queue in which the messages will be stored.
        """
        self.__client = redis_client
        self.__queue_name = queue_name

    async def extract(self) -> ModerationResultSchema:
        """Extract moderation result."""
        result = await self.__client.blpop([self.__queue_name], timeout=None)
        if result is None:
            raise ValueError("No result received from Redis queue.")

        msg = result[1]
        return ModerationResultSchema(**json.loads(msg))


class RedisModerationResultsProducer(BaseModerationResultProducer):
    """Redis-based moderation results Producer."""

    def __init__(
        self, redis_client: redis.asyncio.Redis, queue_name: str = "moderation_results"
    ):
        """
        Init class.

        :param redis_client: Redis client.
        :param queue_name: The names of the queue in which the messages will be stored.
        """
        self.__client = redis_client
        self.__queue_name = queue_name

    async def upload(self, mod_result: ModerationResultSchema) -> None:
        """Upload moderation result."""
        await self.__client.rpush(self.__queue_name, json.dumps(asdict(mod_result)))
