import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config import TOKEN
from app.handlers import router
from app.database.models import async_main

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)

        await dp.feed_update(bot=bot, update=update)

        return web.Response(text="OK")

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return web.Response(status=500)


async def on_startup():
    await async_main()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"🚀 Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown():
    await bot.delete_webhook()
    print("❌ Webhook удалён")


async def start_webhook():
    app = web.Application()

    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # 🔥 ВАЖНО — lifecycle
    app.on_startup.append(lambda app: on_startup())
    app.on_shutdown.append(lambda app: on_shutdown())

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"🌐 Сервер запущен на порту {PORT}")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_webhook())