from .uow import AbstractUnitOfWork
from database import models
from sqlalchemy.exc import IntegrityError

class SectionNotFound(Exception):
    pass

class SectionAlreadyExists(Exception):
    pass

class UserNotFound(Exception):
    pass

class UserAlreadyExists(Exception):
    pass

async def save_survey_result(
    uow: AbstractUnitOfWork, section_title: str, correct_answers_count: int, user_tg_id: int
    ) -> models.Result:
    async with uow:
        questions_count = await uow.question_sections_repo.get_section_questions_count(section_title)
        if questions_count is None:
            raise SectionNotFound(f"Section {section_title} not found")
        user = await uow.user_repo.get_by_tg_id(user_tg_id)
        if user is None:
            raise UserNotFound(f"User {user_tg_id} not found")
        result = models.Result(
            result=(correct_answers_count / questions_count) * 100,
            user_id=user.id,
            section=await uow.question_sections_repo.get_section_by_title(section_title)
        )
        uow.question_sections_repo.add(result)
        await uow.commit()
    return result

async def create_user(
    uow: AbstractUnitOfWork,
    tg_id: int, 
    fname: str,
    lname: str | None,
    username: str | None
) -> models.User:
    async with uow:
        user = models.User(tg_id=tg_id, fname=fname, lname=lname, username=username)
        uow.user_repo.add(user)
        try:
            await uow.commit()
        except IntegrityError:
            raise UserAlreadyExists(f"User {tg_id} already exists")
    return user

async def create_section(
    uow: AbstractUnitOfWork,
    title: str,
) -> models.Section:
    async with uow:
        section = models.Section(title=title)
        uow.question_sections_repo.add(section)
        try:
            await uow.commit()
        except IntegrityError:
            raise SectionAlreadyExists(f"Section {title} already exists")
    return section