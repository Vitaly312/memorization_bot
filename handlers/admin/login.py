from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from middlewares.authorization import CreateUserMiddleware
from load_config import config
import logging
from service.uow import SQLAlchemyUnitOfWork
from service import views, user

router = Router()
router.message.middleware(CreateUserMiddleware())

@router.message(Command('admin', 'a'))
async def cmd_start(message: Message):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if await views.is_user_admin(SQLAlchemyUnitOfWork(), message.from_user.id):
        await message.answer('Вы зарегистрированы как администратор')
        return
    if str(message.from_user.id) in config["APP"]["ADMIN_TG_ID"]:
        await user.make_user_admin(SQLAlchemyUnitOfWork(), message.from_user.id)
        logging.info(f"{str(message.from_user.id)} успешно вошёл в панель управления")
        await message.answer('Вы вошли в панель управления\nВведите /admin_help, чтобы получить справку по командам админ панели')
        return
    logging.info(f"{str(message.from_user.id)} совершил попытку входа в панель управления, неуспешно")
    await message.answer('Вы не являетесь администратором')

@router.message(Command('exit'))
async def cmd_exit(message: Message):
    if await views.is_user_admin(SQLAlchemyUnitOfWork(), message.from_user.id):
        await user.remove_user_admin(SQLAlchemyUnitOfWork(), message.from_user.id)
        await message.answer('Вы вышли из панели управления')
    else:
        await message.answer('Вы не являетесь администратором')

@router.message(Command('admin_help'))
async def cmd_admin_help(message: Message):
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