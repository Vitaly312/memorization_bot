import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import get_info, questions
from handlers.admin import login, edit_questions
from load_config import config
from database.connect import init_models


async def main():
    logging.basicConfig(level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    await init_models()
    bot = Bot(token=config["APP"]["BOT_TOKEN"], parse_mode="HTML")
    dp = Dispatcher()
    dp.include_routers(get_info.router, login.router, questions.router,
                       edit_questions.router)
    await dp.start_polling(bot)

asyncio.run(main())