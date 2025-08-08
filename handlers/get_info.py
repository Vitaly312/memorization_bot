from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from middlewares.authorization import CreateUserMiddleware


router = Router()
router.message.middleware(CreateUserMiddleware())

@router.message(Command('start'))
async def cmd_start(message: Message):
    start_msg = '''Добрый день!
Вы можете пройти опрос, чтобы проверить свои знания или запомнить что-то.
Для того, чтобы увидеть список доступных разделов вопросов, введите команду /start_survey\
, после чего выберите нужный вам раздел.
Для получения справки по доступным командам, введите /help
'''
    await message.answer(start_msg)

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_msg = '''<u>Справка по доступным командам</u>

/start - Перезапуск бота
/start_survey - Выбрать раздел доступных опросов
/info - Результаты прохождения опросов
'''
    await message.answer(help_msg)

