__all__ = ["category", "nya"]

import random
from typing import Any, Literal

from aiogram import Bot
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from .config import Config


async def category(message: Message, config: Config, bot: Bot) -> Literal[False] | dict[str, Any]:
    command_flt = Command(commands=list(config.categories), commands_ignore_case=True)
    result = await command_flt(message, bot)
    if isinstance(result, dict):
        category_name = result["command"].command
        category_ = config.categories[category_name]
        return {**result, "category_name": category_name, "category": category_}
    if result:
        raise AssertionError("command filter returned `True`, not `dict`, this should not happen")
    text = message.text or message.caption
    if not text:
        return False
    for category_name, category_ in config.categories.items():
        message_words = text.split()
        if any(word.startswith(alias) for word in message_words for alias in category_.aliases):
            return {"category_name": category_name, "category": category_}
    return False


async def nya(message: Message) -> bool:
    text = message.text or message.caption
    if not text:
        return False
    message_words = text.split()
    for t in ("ня", "nya"):
        if any(word.startswith(t) for word in message_words):
            return True
        if t in text and random.random() < 0.1:  # 10% chance
            return True
    return False
