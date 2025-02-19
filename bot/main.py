"""The module responsible for setting up and running the bot."""

import asyncio
import logging
import logging.config
from typing import Any, Dict

import redis.asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from producer_consumer.messages.redis_pc import RedisMessageProducer
from producer_consumer.moderation_results.redis_pc import RedisModerationResultsConsumer

from .config.bot_config import BotConfig, get_config
from .config.log_config import get_log_config
from .handlers.moderation import router as moderation_router
from .middlewares.msg_producer_middleware import MsgProducerMiddleware
from .services.post_moderation import PostModerationManager


async def main():
    """Config and launch bot."""
    # config
    config: BotConfig = get_config()

    # logging
    log_config: Dict[str, Any] = get_log_config(config)
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("bot")

    # bot
    bot: Bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp: Dispatcher = Dispatcher()

    # Redis client
    client = None
    pool = None
    try:
        pool = redis.asyncio.ConnectionPool.from_url(config.redis.url)
        client = redis.asyncio.Redis(connection_pool=pool)

        # message producer
        msg_producer = RedisMessageProducer(redis_client=client)

        # moderation results consumer
        mod_res_consumer = RedisModerationResultsConsumer(redis_client=client)

        # post-moderation
        post_moderation_manager = PostModerationManager(bot, config, mod_res_consumer)

        # init middlewares
        msg_producer_middleware = MsgProducerMiddleware(msg_producer)

        # register routers
        dp.include_router(moderation_router)

        # register middlewares for routers
        moderation_router.message.middleware(msg_producer_middleware)

        # launch bot and launch post-moderation
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Startup")
        await asyncio.gather(dp.start_polling(bot), post_moderation_manager.run())
    finally:
        if client is not None:
            await client.close()
        if pool is not None:
            await pool.aclose()


if __name__ == "__main__":
    asyncio.run(main())
