from database.connect import async_session
from .repo import (AbstractQuestionSectionsReporistory, SQLAlchemyQuestionSectionsRepository,
                   AbstractUserRepository,
                   SQLAlchemyUserRepository)
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


DEFAULT_SESSIONFACTORY = async_session


class AbstractUnitOfWork(ABC):
    question_sections_repo: AbstractQuestionSectionsReporistory
    user_repo: AbstractUserRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self
    
    async def __aexit__(self, *args):
        await self.rollback()
    
    @abstractmethod
    async def commit():
        raise NotImplementedError
    
    @abstractmethod
    async def rollback():
        raise NotImplementedError
    
class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    session: AsyncSession

    def __init__(self, session_factory=DEFAULT_SESSIONFACTORY, session: AsyncSession = None):
        self.session_factory = session_factory
        self.session = session

    async def __aenter__(self):
        if self.session is None:
            self.session = self.session_factory()
        self.question_sections_repo = SQLAlchemyQuestionSectionsRepository(self.session)
        self.user_repo = SQLAlchemyUserRepository(self.session)
        return self

    async def commit(self):
        await self.session.commit()

    def delete_session(self):
        self.session = None
    
    async def rollback(self):
        await self.session.rollback()
