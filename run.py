import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import TOKEN
from app.handlers import router
from app.database.models import async_main

# 🔧 настройки
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "supersecret"  # можешь оставить
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render сам даст URL
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def on_startup(app):
    await async_main()
    dp.include_router(router)

    # ставим webhook
    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET
    )
    print("Webhook set:", WEBHOOK_URL)


async def on_shutdown(app):
    await bot.delete_webhook()
    print("Webhook deleted")


def main():
    logging.basicConfig(level=logging.INFO)

    app = web.Application()

    # регистрируем webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()