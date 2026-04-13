import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config import TOKEN
from app.handlers import router
from app.database.models import async_main

# =====================
# НАСТРОЙКИ
# =====================

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 10000))

# =====================
# БОТ
# =====================

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

# =====================
# WEBHOOK HANDLER
# =====================

async def handle_webhook(request):
    try:
        data = await request.json()

        # 🔥 ВАЖНО: правильное преобразование
        update = Update.model_validate(data)

        await dp.feed_update(bot=bot, update=update)

        return web.Response(text="OK")

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return web.Response(status=500)

# =====================
# ЗАПУСК СЕРВЕРА
# =====================

async def start_webhook():
    await async_main()

    # ставим webhook
    await bot.set_webhook(WEBHOOK_URL)

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"🚀 Webhook запущен: {WEBHOOK_URL}")

    while True:
        await asyncio.sleep(3600)

# =====================
# MAIN
# =====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_webhook())