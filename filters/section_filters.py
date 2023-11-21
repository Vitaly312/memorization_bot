from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from database.connect import get_conn
from database.models import Section
from sqlalchemy import select


class SectionExistFilter(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        async with get_conn() as session:
            result = await session.execute(select(Section.title))
            return cb.data in result.scalars()