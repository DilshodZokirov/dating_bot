import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo

from app.bot.handlers import router
from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    storage = RedisStorage.from_url(settings.redis_url)
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    if settings.webapp_url:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Qidirish", web_app=WebAppInfo(url=f"{settings.webapp_url}/webapp/"))
        )
    else:
        logging.warning("WEBAPP_URL sozlanmagan — Menu tugmasi Mini App'ga ulanmadi")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
