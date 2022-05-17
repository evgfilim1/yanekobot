__all__ = ["root_router"]

import logging
import random
from urllib.parse import urljoin

from aiogram import Router
from aiogram.methods import TelegramMethod
from aiogram.types import InlineQuery, InlineQueryResult, InlineQueryResultPhoto, Message

from .config import CategoryConfig, Config, StorageConfig
from .filters import category as category_filter
from .filters import nya as nya_filter

root_router = Router()


@root_router.message(nya_filter)
async def send_nya(message: Message) -> TelegramMethod[Message]:
    cat_kaomoji = random.choice(
        (
            "^.^",
            "^_^",
            "ฅ(＾・ω・＾ฅ)",
            "(=^･ω･^=)",
            "/ᐠ. ᴗ.ᐟ\\",
            "/ᐠܻ    ᳕⑅ܻ ᐟ\\ﾉ",
            " —ฅ/ᐠ. ̫ .ᐟ\\ฅ —",
            "ฅ^•ﻌ•^ฅ",  # RTL warning
            "^•^",
            "U^ｪ^U",
            "/ᐠ｡ꞈ｡ᐟ\\",
            "(=^･ｪ･^=)",
            "(^._.^)ﾉ",
            "=＾● ⋏ ●＾=",
            "(̷ ̷₌̷ ̷ㅇ̷ ̷ᆽ̷ ̷ㅇ̷ ̷₌̷ ̷)♡",
            "(=^‥^=)",
            "＼(=^‥^)/’` |",
            "(=^･ｪ･^=))ﾉ彡☆",
            "(^=◕ᴥ◕=^)",
            "ヽ(^‥^=ゞ)",
            "(^=˃ᆺ˂)",
            "ि०॰͡०ी",
        )
    )
    return message.answer(cat_kaomoji)


async def _get_random_picture_name(category_name: str, storage: StorageConfig) -> str | None:
    category_dir = storage.base_path / "pictures" / category_name
    if not category_dir.exists():
        return None
    try:
        picture = random.choice(list(category_dir.iterdir()))
    except IndexError:
        return None
    return picture.name


@root_router.message(category_filter)
async def send_picture(
    message: Message,
    category: CategoryConfig,
    category_name: str,
    config: Config,
) -> TelegramMethod[Message]:
    pic = await _get_random_picture_name(category_name, config.storage)
    if pic is None and not category.hidden:
        return message.reply(f"No pictures of {category_name} saved yet :(")
    url = urljoin(str(config.storage.url), f"{category_name}/{pic}")
    logging.warning(f"Sending picture {url!r}")
    return message.reply_photo(
        url,
        caption=random.choice(category.captions or [""]),
    )


@root_router.inline_query()
async def send_picture_inline(
    query: InlineQuery,
    config: Config,
) -> TelegramMethod[bool]:
    answers: list[InlineQueryResult] = []
    for category_name in config.categories:
        pic = await _get_random_picture_name(category_name, config.storage)
        if pic is None:
            continue
        category = config.categories[category_name]
        pic_path = f"{category_name}/{pic}"
        url = urljoin(str(config.storage.url), pic_path)
        answers.append(
            InlineQueryResultPhoto(
                id=pic_path,
                photo_url=url,
                thumb_url=url,
                caption=random.choice(category.captions or [""]),
            ),
        )
    return query.answer(answers, cache_time=1, is_personal=True)
