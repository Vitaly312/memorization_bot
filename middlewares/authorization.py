from aiogram import BaseMiddleware
from aiogram.types import Message
from database.models import User
from database.connect import get_conn
from datetime import datetime

class AuthorizeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        with get_conn() as session:
            user = session.query(User).filter(User.tg_id == event.from_user.id).first()
            if not user:
                user = User(tg_id=event.from_user.id,
                            fname=event.from_user.first_name,
                            lname=event.from_user.last_name,
                            username=event.from_user.username
                            )
            user.last_login = datetime.now()
            session.add(user)
            session.commit()
            data['user'] = user
            data['session'] = session
            result = await handler(event, data)
            session.commit()
        return result