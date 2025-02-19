"""The module responsible for the handlers for moderation."""

from aiogram import Router
from aiogram.types import Message

from producer_consumer.messages.base import BaseMessageProducer
from schemas.messages import MessageSchema

router: Router = Router()


@router.message()
async def moderate_message(msg: Message, msg_producer: BaseMessageProducer):
    """Add a message to the moderation queue."""
    msg_schema: MessageSchema = MessageSchema(id=str(msg.message_id), text=msg.text)
    await msg_producer.upload(msg_schema)
