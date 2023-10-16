from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from middlewares.authorization import AuthorizeMiddleware
from database.models import User
from load_config import config
from sqlalchemy.orm import Session


router = Router()
router.message.middleware(AuthorizeMiddleware())

@router.message(Command('admin', 'a'))
async def cmd_start(message: Message, user: User, session: Session):
    if user.is_admin:
        await message.answer('Вы зарегестрированны как администратор')
        return
    if str(message.from_user.id) in config["APP"]["ADMIN_TG_ID"]:
        user.is_admin = True
        session.add(user)
        await message.answer('Вы вошли в панель управления\nВведите /admin_help, чтобы получть справку по командам админ панели')
        return
    await message.answer('Вы не являетесь администратором')

@router.message(Command('exit'))
async def cmd_exit(message: Message, user: User, session: Session):
    if user.is_admin:
        user.is_admin = False
        session.add(user)
        await message.answer('Вы вышли из панели управления')
    else:
        await message.answer('Вы не являетесь администратором')

@router.message(Command('admin_help'))
async def cmd_admin_help(message: Message, user: User):
    admin_help_msg = f'''
<u><b>Справка по командам админ панели</b></u>

/admin; /a - Войти в админ панель(доступ только с разрешенных telegram id)
/exit - Выйти из админ панели
/list_sections - Список существующих разделов вопросов
/create_section {html.quote('<название раздела>')} - Создать новый раздел вопросов с указанным названием
/delete_section {html.quote('<id раздела>')} - Удалить раздел вопросов с указанным id
/list_questions {html.quote('<id раздела>')} - Список вопросов в разделе с указанным id
/create_question - Добавить новый вопрос в один из существующих разделов
/delete_question {html.quote('<id вопроса>')} - Удалить вопрос с указанным id
'''
    await message.answer(admin_help_msg)