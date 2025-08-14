from aiogram import BaseMiddleware, Router
from aiogram.types import Message
from service import views, use_cases
from service.uow import SQLAlchemyUnitOfWork
import os


class CreateUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        if not await views.is_user_exists(
            data["uow"], data["redis"], event.from_user.id
        ):
            await use_cases.create_user(
                data["uow"],
                tg_id=event.from_user.id,
                fname=event.from_user.first_name,
                lname=event.from_user.last_name,
                username=event.from_user.username,
            )
        return await handler(event, data)


class UnplugTgAnswersMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        async def fake_answer(*args, **kwargs):
            pass

        event.__dict__["answer"] = fake_answer
        if hasattr(event, "message"):
            event.message.__dict__["answer"] = fake_answer
        return await handler(event, data)


class InjectUoWMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        data["uow"] = SQLAlchemyUnitOfWork()
        return await handler(event, data)


def setup_middlewares(router: Router):
    if os.getenv("UNPLUG_TG_ANSWERS") == "1":
        router.message.middleware(UnplugTgAnswersMiddleware())
        router.callback_query.middleware(UnplugTgAnswersMiddleware())
    router.message.middleware(InjectUoWMiddleware())
    router.callback_query.middleware(InjectUoWMiddleware())
    router.message.middleware(CreateUserMiddleware())
    router.callback_query.middleware(CreateUserMiddleware())
