from aiogram import BaseMiddleware
from aiogram.types import Message


class IsAdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        user = data['user']
        if not user.is_admin:
            return await event.answer('Вы не являетесь администратором')
        return await handler(event, data)