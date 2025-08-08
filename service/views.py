from .uow import SQLAlchemyUnitOfWork
from database import models
from sqlalchemy import select, func
from dataclasses import dataclass
from datetime import datetime, timedelta

async def get_section_titles(uow: SQLAlchemyUnitOfWork) -> list[str]:
    async with uow:
        return (await uow.session.scalars(
            select(models.Section.title)
        )).all()

@dataclass
class QuestionAndAnswer:
    question: str
    answer: str

@dataclass
class SectionStat:
    section_title: str
    day_result: float | None # none means that section has no results for today
    total_result: float | None


async def get_section_questions_and_answers(uow: SQLAlchemyUnitOfWork,
                    section_title: str) -> list[QuestionAndAnswer]:
    async with uow:
        return (await uow.session.scalars(
            select(models.Question.question, models.Question.answer)
            .join(models.Section)
            .where(models.Section.title == section_title)
        )).all()

async def get_section_answers_count(uow: SQLAlchemyUnitOfWork,
                    section_title: str) -> int:
    async with uow:
        return await uow.session.scalar(
            select(func.count(models.Question.answer))
            .join(models.Section)
            .where(models.Section.title == section_title)
        )

async def get_stat(uow: SQLAlchemyUnitOfWork, user_tg_id: int) -> list[SectionStat]:
    yesterday = datetime.now() - timedelta(days=1)
    async with uow:
        all_sections = (await uow.session.scalars(
            select(models.Section.title)
        )).all()

        total_results = await uow.session.execute(
            select(models.Section.title, func.avg(models.Result.result))
            .join(models.Result)
            .where(models.Result.user_id == user_tg_id)
            .group_by(models.Section.title),
        )
        total_data = {row[0]: row[1] for row in total_results.fetchall()}

        day_results = await uow.session.execute(
            select(models.Section.title, func.avg(models.Result.result))
            .join(models.Result)
            .where(models.Result.user_id == user_tg_id)
            .where(models.Result.created_on > yesterday)
            .group_by(models.Section.title),
        )
        day_data = {row[0]: row[1] for row in day_results.fetchall()}

        return [
            SectionStat(
                section_title=title,
                total_result=total_data.get(title),
                day_result=day_data.get(title)
            )
            for title in all_sections
        ]

async def is_user_exists(uow: SQLAlchemyUnitOfWork, user_tg_id: int) -> bool:
    async with uow:
        return await uow.session.scalar(
            select(models.User.id).where(models.User.tg_id == user_tg_id)
        ) is not None