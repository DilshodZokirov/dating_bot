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
        # Global default — bitta kirish: Menu. Matn /start da foydalanuvchi tiliga moslanadi.
        menu_url = f"{settings.webapp_url.rstrip('/')}/webapp/?v=onesearch1"
        logging.info("Setting menu button: %s", menu_url)
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="Qidirish", web_app=WebAppInfo(url=menu_url))
            )
        except Exception as e:
            logging.error("Menu button o'rnatilmadi: %s", e)
    else:
        logging.warning("WEBAPP_URL sozlanmagan — Menu tugmasi Mini App'ga ulanmadi")

    logging.info("WEBAPP_URL=%r LIVEKIT=%s", settings.webapp_url, bool(settings.livekit_url))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
