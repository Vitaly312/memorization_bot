from service.uow import AbstractUnitOfWork
from service.repo import (
    AbstractRepository,
    AbstractQuestionSectionsReporistory,
    AbstractUserRepository,
)
from database import models
import pytest
from service import questions, exceptions


class FakeRepository[T](AbstractRepository[T]):
    models: list[T]

    def __init__(self):
        self.models = []

    def add(self, obj: T) -> T:
        self.models.append(obj)
        return obj

    async def get(self, id: int) -> T | None:
        return next((model for model in self.models if model.id == id), None)

    async def get_all(self) -> list[T]:
        return self.models

    def delete(self, obj: T) -> None:
        self.models.remove(obj)

class FakeQuestionSectionsRepository(
    AbstractQuestionSectionsReporistory, FakeRepository[models.Section]
):
    async def get_section_questions_count(self, section_title: str) -> int | None:
        return next(
            (
                len(model.questions)
                for model in self.models
                if model.title == section_title
            ),
            None,
        )

    async def get_section_by_title(self, section_title: str) -> models.Section | None:
        return next((model for model in self.models if model.title == section_title), None)


class FakeUserRepository(AbstractUserRepository, FakeRepository[models.User]):
    async def get_by_tg_id(self, tg_id: int) -> models.User | None:
        return next((model for model in self.models if model.tg_id == tg_id), None)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.question_sections_repo = FakeQuestionSectionsRepository()
        self.user_repo = FakeUserRepository()

    async def commit(self):
        pass

    async def rollback(self):
        pass


@pytest.mark.asyncio
async def test_saved_result_has_correct_percent():
    uow = FakeUnitOfWork()
    uow.question_sections_repo.add(
        models.Section(
            title="test",
            questions=[
                models.Question(question="question", answer="answer")
                for _ in range(100)
            ],
        )
    )
    uow.user_repo.add(models.User(tg_id=1, fname="test", lname="test", username="test"))
    result = await questions.save_survey_result(uow, "test", 50, 1)
    assert result.result == 50

@pytest.mark.asyncio
async def test_save_result_raise_exception_if_section_not_found():
    uow = FakeUnitOfWork()
    uow.user_repo.add(models.User(tg_id=1, fname="test", lname="test", username="test"))
    with pytest.raises(exceptions.SectionNotFoundException):
        await questions.save_survey_result(uow, "test", 50, 1)

@pytest.mark.asyncio
async def test_save_result_raise_exception_if_user_not_found():
    uow = FakeUnitOfWork()
    uow.question_sections_repo.add(models.Section(title="test"))
    with pytest.raises(exceptions.UserNotFoundException):
        await questions.save_survey_result(uow, "test", 50, 1)