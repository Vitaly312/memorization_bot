import asyncio
from aiogram import Bot, Dispatcher
from handlers import get_info, questions
from handlers.admin import login, edit_questions
from load_config import config


async def main():
    bot = Bot(token=config["APP"]["BOT_TOKEN"], parse_mode="HTML")
    dp = Dispatcher()
    dp.include_routers(get_info.router, login.router, questions.router,
                       edit_questions.router)
    await dp.start_polling(bot)

asyncio.run(main())