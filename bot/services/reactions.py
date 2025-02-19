"""The module responsible for responding to messages."""

from typing import Dict

from aiogram.types.reaction_type_custom_emoji import ReactionTypeCustomEmoji

REACTION: Dict[str, ReactionTypeCustomEmoji] = {
    "generated_by_llm": ReactionTypeCustomEmoji(custom_emoji_id="👾"),
    "toxic": ReactionTypeCustomEmoji(custom_emoji_id="🤮"),
}
