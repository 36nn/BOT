import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web

from config import TOKEN
from app.handlers import router
from app.database.models import async_main

# ===== НАСТРОЙКИ =====
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "supersecret"  # любое слово
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render сам подставляет
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== WEBHOOK HANDLER =====
async def handle_webhook(request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=403)

    data = await request.json()
    await dp.feed_update(bot=bot, update=data)
    return web.Response()

# ===== STARTUP =====
async def on_startup(app):
    await async_main()
    dp.include_router(router)

    await bot.set_webhook(
        WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET
    )

# ===== SHUTDOWN =====
async def on_shutdown(app):
    await bot.delete_webhook()

# ===== APP =====
def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app

# ===== RUN =====
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = create_app()
    web.run_app(app, port=int(os.environ.get("PORT", 10000)))