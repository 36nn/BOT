import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web

from config import TOKEN
from app.handlers import router
from app.database.models import async_main


# ------------------ БОТ ------------------
bot = Bot(token=TOKEN)
dp = Dispatcher()


# ------------------ ВЕБ-СЕРВЕР (анти-сон) ------------------
async def handle(request):
    return web.Response(text="Бот работает ✅")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))  # Render требует PORT

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"🌐 Web server started on port {port}")


# ------------------ MAIN ------------------
async def main():
    await async_main()  # создаём БД

    dp.include_router(router)

    # 🔥 запускаем веб-сервер (анти-сон)
    await start_web_server()

    # 🔥 запускаем бота
    await dp.start_polling(bot)


# ------------------ ЗАПУСК ------------------
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен ❌")