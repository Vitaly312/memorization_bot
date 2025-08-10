from abc import ABC, abstractmethod
from database import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase


class AbstractRepository[T: DeclarativeBase](ABC):
    @abstractmethod
    def add(self, obj: T):
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj: T) -> None:
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

class AbstractQuestionRepository(AbstractRepository[models.Question]):
    pass

class SQLAlchemyRepository[T: DeclarativeBase](AbstractRepository[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, obj: T) -> T:
        self.session.add(obj)
        return obj

    async def get(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self) -> list[T]:
        return (await self.session.scalars(select(self.model))).all()

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)

class SQLAlchemySectionsRepository(
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

class SQLAlchemyQuestionsRepository(
    SQLAlchemyRepository[models.Question], AbstractQuestionRepository
):
    model = models.Question