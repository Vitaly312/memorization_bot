from aiogram import BaseMiddleware
from aiogram.types import Message
from database.models import User
from database.connect import get_conn
from datetime import datetime
from sqlalchemy import select, update
from service import views, questions
from service.uow import SQLAlchemyUnitOfWork
import logging


class CreateUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        uow = SQLAlchemyUnitOfWork()
        if not await views.is_user_exists(uow, event.from_user.id):
            await questions.create_user(uow, 
                tg_id=event.from_user.id,
                fname=event.from_user.first_name,
                lname=event.from_user.last_name,
                username=event.from_user.username)
        return await handler(event, data)

class AuthorizeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data) -> bool:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        async with get_conn() as session:
            stmt = select(User).where(User.tg_id == event.from_user.id)
            result = await session.execute(stmt)
            user = result.scalar()
            if not user:
                user = User(tg_id=event.from_user.id,
                            fname=event.from_user.first_name,
                            lname=event.from_user.last_name,
                            username=event.from_user.username
                            )
                session.add(user)
                logger.info('New user')
            stmt = update(User).where(User.id==user.id).values(last_login=datetime.now())
            await session.execute(stmt)
            data['user'] = user
            data['session'] = session
            result = await handler(event, data)
            await session.commit()
        return result