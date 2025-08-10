from database.connect import async_session
from .repo import (AbstractQuestionSectionsReporistory, SQLAlchemySectionsRepository,
                   AbstractUserRepository, SQLAlchemyUserRepository,
                   AbstractQuestionRepository, SQLAlchemyQuestionsRepository)
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


DEFAULT_SESSIONFACTORY = async_session


class AbstractUnitOfWork(ABC):
    question_sections_repo: AbstractQuestionSectionsReporistory
    user_repo: AbstractUserRepository
    question_repo: AbstractQuestionRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self
    
    async def __aexit__(self, *args):
        await self.rollback()
    
    @abstractmethod
    async def commit(self):
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
    
class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    session: AsyncSession

    def __init__(self, session_factory=DEFAULT_SESSIONFACTORY, session: AsyncSession | None = None,
            skip_rollback_on_exit: bool = False):
        self.session_factory = session_factory
        self.session = session
        self.skip_rollback_on_exit = skip_rollback_on_exit

    async def __aenter__(self):
        if self.session is None:
            self.session = self.session_factory()
        self.question_sections_repo = SQLAlchemySectionsRepository(self.session)
        self.user_repo = SQLAlchemyUserRepository(self.session)
        self.question_repo = SQLAlchemyQuestionsRepository(self.session)
        return self

    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()

    async def __aexit__(self, *args):
        if not self.skip_rollback_on_exit:
            await self.rollback()
