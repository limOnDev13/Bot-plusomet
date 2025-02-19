"""The module responsible for schemas for working with messages."""

from dataclasses import dataclass


@dataclass
class MessageSchema(object):
    """The scheme of the message for subsequent moderation."""

    id: str
    text: str


@dataclass
class ModerationResultSchema(object):
    """The structure of the LLM response after message moderation."""

    msg_id: str
    generated_by_llm: bool
    toxic: bool
