import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from database.connect import init_models, engine
from handlers import get_info, questions
from handlers.admin import login, edit_questions
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from typing import Any
import uvicorn
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()

    dp.include_routers(
        get_info.router, login.router, questions.router, edit_questions.router
    )
    bot_webhook = await bot.get_webhook_info()
    if bot_webhook.url != os.getenv("BOT_WEBHOOK_URL"):
        await bot.set_webhook(
            os.getenv("BOT_WEBHOOK_URL"),
            allowed_updates=["message", "callback_query"])

    yield
    await engine.dispose()
    await bot.session.close()

load_dotenv()
logging.basicConfig(
    level=logging.WARNING,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

redis = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))

app = FastAPI(lifespan=lifespan)
dp = Dispatcher(storage=RedisStorage(redis=redis), redis=redis)
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))


@app.post("/webhook")
async def webhook(request: dict[Any, Any]):
    await dp.feed_raw_update(bot, request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
