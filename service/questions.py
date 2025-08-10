from .uow import AbstractUnitOfWork
from database import models
from .exceptions import (
    SectionNotFoundException,
    QuestionNotFoundException,
    UserNotFoundException,
)


async def save_survey_result(
    uow: AbstractUnitOfWork, section_title: str, correct_answers_count: int, user_tg_id: int
    ) -> models.Result:
    async with uow:
        questions_count = await uow.question_sections_repo.get_section_questions_count(section_title)
        if questions_count is None:
            raise SectionNotFoundException(f"Section {section_title} not found")
        user = await uow.user_repo.get_by_tg_id(user_tg_id)
        if user is None:
            raise UserNotFoundException(f"User {user_tg_id} not found")
        result = models.Result(
            result=(correct_answers_count / questions_count) * 100,
            user_id=user.id,
            section=await uow.question_sections_repo.get_section_by_title(section_title)
        )
        uow.question_sections_repo.add(result)
        await uow.commit()
    return result

async def create_question(
    uow: AbstractUnitOfWork,
    question: str,
    answer: str,
    section_id: int,
) -> models.Question:
    async with uow:
        section = await uow.question_sections_repo.get(section_id)
        if section is None:
            raise SectionNotFoundException(f"Section {section_id} not found")
        question_model = models.Question(question=question, answer=answer, section=section)
        uow.question_repo.add(question_model)
        await uow.commit()
    return question_model

async def delete_question(
    uow: AbstractUnitOfWork,
    question_id: int,
) -> None:
    async with uow:
        question = await uow.question_repo.get(question_id)
        if question is None:
            raise QuestionNotFoundException(f"Question {question_id} not found")
        await uow.question_repo.delete(question)
        await uow.commit()
