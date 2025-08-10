from aiogram import BaseMiddleware
from aiogram.types import Message
from service import views, use_cases
from service.uow import SQLAlchemyUnitOfWork

class CreateUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        uow = SQLAlchemyUnitOfWork()
        if not await views.is_user_exists(uow, event.from_user.id):
            await use_cases.create_user(uow, 
                tg_id=event.from_user.id,
                fname=event.from_user.first_name,
                lname=event.from_user.last_name,
                username=event.from_user.username)
        return await handler(event, data)
