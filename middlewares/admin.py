from aiogram import BaseMiddleware
from aiogram.types import Message
from service import views

class IsAdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        is_admin = await views.is_user_admin(data["uow"], event.from_user.id)
        if not is_admin:
            return await event.answer('Вы не являетесь администратором')
        return await handler(event, data)