from abc import ABC, abstractmethod
from database import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


class AbstractRepository[T](ABC):
    @abstractmethod
    def add(self, obj: T):
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> T | None:
        raise NotImplementedError


class AbstractQuestionSectionsReporistory(AbstractRepository[models.Section]):
    @abstractmethod
    async def get_section_questions_count(self, section_title: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    async def get_section_by_title(self, section_title: str) -> models.Section | None:
        raise NotImplementedError


class AbstractUserRepository(AbstractRepository[models.User]):
    @abstractmethod
    async def get_by_tg_id(self, tg_id: int) -> models.User | None:
        raise NotImplementedError

class SQLAlchemyRepository[T](AbstractRepository[T]):
    model: T

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, obj: T) -> T:
        self.session.add(obj)
        return obj

    async def get(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

class SQLAlchemyQuestionSectionsRepository(
    SQLAlchemyRepository[models.Section], AbstractQuestionSectionsReporistory
):
    model = models.Section
    
    async def get_section_questions_count(self, section_title: str) -> int | None:
        return await self.session.scalar(
            select(func.count(models.Question.answer))
            .join(models.Section)
            .where(
                models.Section.title == section_title
            )
        )

    async def get_section_by_title(self, section_title: str) -> models.Section | None:
        return await self.session.scalar(
            select(models.Section).where(models.Section.title == section_title)
        )

class SQLAlchemyUserRepository(
    SQLAlchemyRepository[models.User], AbstractUserRepository
):
    model = models.User

    async def get_by_tg_id(self, tg_id):
        return await self.session.scalar(
            select(models.User).where(models.User.tg_id == tg_id)
        )
