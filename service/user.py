from service.uow import AbstractUnitOfWork
from service.exceptions import UserNotFoundException, UserAlreadyExistsException
from database import models
from sqlalchemy.exc import IntegrityError

async def create_user(
    uow: AbstractUnitOfWork,
    tg_id: int, 
    fname: str,
    lname: str | None,
    username: str | None
) -> models.User:
    async with uow:
        user = models.User(tg_id=str(tg_id), fname=fname, lname=lname, username=username)
        uow.user_repo.add(user)
        try:
            await uow.commit()
        except IntegrityError as e:
            print(e)
            raise UserAlreadyExistsException(f"User {tg_id} already exists")
    return user

async def make_user_admin(
    uow: AbstractUnitOfWork,
    user_tg_id: int,
) -> None:
    async with uow:
        user = await uow.user_repo.get_by_tg_id(user_tg_id)
        if user is None:
            raise UserNotFoundException(f"User {user_tg_id} not found")
        user.is_admin = True
        await uow.commit()

async def remove_user_admin(
    uow: AbstractUnitOfWork,
    user_tg_id: int,
) -> None:
    async with uow:
        user = await uow.user_repo.get_by_tg_id(user_tg_id)
        if user is None:
            raise UserNotFoundException(f"User {user_tg_id} not found")
        user.is_admin = False
        await uow.commit()