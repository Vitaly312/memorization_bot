from service.uow import AbstractUnitOfWork
from service.exceptions import SectionAlreadyExistsException, SectionNotFoundException
from database import models
from sqlalchemy.exc import IntegrityError


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
            raise SectionAlreadyExistsException(f"Section {title} already exists")
    return section

async def delete_section(
    uow: AbstractUnitOfWork,
    section_title: str,
) -> None:
    async with uow:
        section = await uow.question_sections_repo.get_section_by_title(section_title)
        if section is None:
            raise SectionNotFoundException(f"Section {section_title} not found")
        await uow.question_sections_repo.delete(section)
        await uow.commit()