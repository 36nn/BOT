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

BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
if not BASE_URL:
    raise ValueError("RENDER_EXTERNAL_URL не найден")

WEBHOOK_URL = BASE_URL + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 10000))

# =====================
# БОТ
# =====================

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

# =====================
# HANDLERS
# =====================

# 🔥 webhook
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)

        await dp.feed_update(bot=bot, update=update)

        return web.Response(text="OK")

    except Exception as e:
        print("❌ WEBHOOK ERROR:", e)
        return web.Response(status=500)


# 🔥 health check (для Render)
async def health(request):
    return web.Response(text="OK")


# =====================
# LIFECYCLE
# =====================

async def on_startup(app):
    await async_main()

    # ставим webhook
    await bot.set_webhook(WEBHOOK_URL)
    print(f"🚀 Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.delete_webhook()
    print("❌ Webhook удалён")


# =====================
# СЕРВЕР
# =====================

async def start_webhook():
    app = web.Application()

    # маршруты
    app.router.add_get("/", health)
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # lifecycle
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"🌐 Сервер запущен на порту {PORT}")

    # держим сервер живым
    while True:
        await asyncio.sleep(3600)


# =====================
# АНТИ-КРАШ
# =====================

async def main():
    while True:
        try:
            await start_webhook()
        except Exception as e:
            print("🔥 CRASH:", e)
            print("⏳ Перезапуск через 5 секунд...")
            await asyncio.sleep(5)


# =====================
# START
# =====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())