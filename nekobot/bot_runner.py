__all__ = ["run_polling", "run_webhook"]

from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from .config import Config
from .handlers import root_router


def _setup(token: str, server: str | None) -> Bot:
    bot = Bot(token=token, parse_mode="HTML")
    if server is not None:
        bot.session.api = TelegramAPIServer.from_base(server, is_local=True)
    return bot


async def _set_webhook(bot: Bot, webhook_url: str) -> None:
    await bot.set_webhook(webhook_url)


async def _delete_webhook(bot: Bot) -> None:
    await bot.delete_webhook()


def run_polling(config: Config) -> None:
    dp = Dispatcher()
    dp.include_router(root_router)
    dp.startup.register(_delete_webhook)

    bot = _setup(config.bot.token, config.bot.api_url)

    dp.run_polling(bot, config=config)


def run_webhook(config: Config, host: str, port: int, path: str, url: str) -> None:
    dp = Dispatcher()
    dp.include_router(root_router)
    dp.startup.register(_set_webhook)

    bot = _setup(config.bot.token, config.bot.api_url)

    webapp = web.Application()
    SimpleRequestHandler(dp, bot, config=config, webhook_url=url).register(webapp, path=path)
    web.run_app(webapp, host=host, port=port, path=path)
