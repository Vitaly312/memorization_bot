import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers import get_info, questions
from handlers.admin import login, edit_questions
from database.connect import init_models, engine
import os
from dotenv import load_dotenv

async def on_shutdown(bot: Bot):
    await engine.dispose()
    await bot.session.close()

async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    await init_models()
    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(get_info.router, login.router, questions.router,
                       edit_questions.router)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)

asyncio.run(main())