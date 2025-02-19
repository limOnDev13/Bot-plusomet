"""The module responsible for starting moderation."""

import asyncio
import logging.config
from logging import getLogger
from typing import Any, Dict

import redis.asyncio
from dotenv import load_dotenv

from producer_consumer.messages.redis_pc import RedisMessageConsumer
from producer_consumer.moderation_results.redis_pc import RedisModerationResultsProducer

from .config.app_config import Config, get_config
from .config.log_config import get_log_config
from .services.api.llm.yandex_gpt import YandexGPTAPI
from .services.moderation import ModerationManager
from .services.moderators.llm_moderator import LLMModerator


async def main():
    """Start moderation."""
    # config
    load_dotenv()
    config: Config = get_config()

    # logging
    log_config: Dict[str, Any] = get_log_config(config)
    logging.config.dictConfig(log_config)
    logger = getLogger("main")

    # LLM API
    llm_api: YandexGPTAPI = YandexGPTAPI(config)

    # LLM Moderator
    moderator: LLMModerator = LLMModerator(
        llm_api=llm_api, config=config.moderation_config
    )

    # Redis client
    client = None
    pool = None
    try:
        pool = redis.asyncio.ConnectionPool.from_url(config.redis.url)
        client = redis.asyncio.Redis(connection_pool=pool)

        msg_consumer = RedisMessageConsumer(client)
        mod_res_produces = RedisModerationResultsProducer(client)

        moderation_manager = ModerationManager(
            msg_consumer=msg_consumer,
            mod_res_producer=mod_res_produces,
            moderator=moderator,
        )

        # run moderation
        logger.info("Start moderation.")
        await moderation_manager.run()

    finally:
        if client is not None:
            await client.close()
        if pool is not None:
            await pool.aclose()


if __name__ == "__main__":
    asyncio.run(main())
