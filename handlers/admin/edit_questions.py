from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from database.models import Question, Section
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from middlewares.authorization import AuthorizeMiddleware
from middlewares.admin import IsAdminMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.message.middleware(IsAdminMiddleware())

class CreateQuestion(StatesGroup):
    create_question = State()
    create_answer = State()
    select_section = State()

@router.message(Command('list_sections'))
async def cmd_list_sections(message: Message, session: AsyncSession):
    result = await session.execute(select(Section))
    query = result.scalars()
    if not query:
        await message.answer('На данный момент разделы не существуют')
    else:
        msg = '<u>Список разделов:</u>\n(В формате ID - название раздела)\n\n'
        for session in query.all():
            msg += f"{session.id} - {session.title}\n"
        await message.answer(msg, parse_mode = "HTML")

@router.message(Command('create_section'))
async def cmd_create_section(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.answer("Необходимо указать название раздела")
        return
    try:
        section = Section(title=command.args)
        session.add(section)
        await session.commit()
        await message.answer(f"Раздел с названием {command.args} успешно создан")
    except IntegrityError:
        await session.rollback()
        await message.answer('Раздел с таким названием уже существует. Выберите другое название раздела')

@router.message(Command('delete_section'))
async def cmd_delete_section(message: Message, command: CommandObject, session: AsyncSession):
    section = await session.get(Section, command.args)
    if not section:
        await message.answer('Раздела с указанным id не существует')
    else:
        await session.delete(section)
        await message.answer(f"Раздел с id {command.args} успешно удалён")

@router.message(Command('create_question'))
async def cmd_new_question(message: Message, state: FSMContext):
    await message.answer('Напишите вопрос')
    await state.set_state(CreateQuestion.create_question)

@router.message(CreateQuestion.create_question, F.text)
async def cmd_create_answer(message: Message, state: FSMContext):
    await state.update_data({'question': message.text})
    await message.answer('Напишите ответ к вопросу')
    await state.set_state(CreateQuestion.create_answer)

@router.message(CreateQuestion.create_answer, F.text)
async def cmd_create_question(message: Message, state: FSMContext):
    await state.update_data({'answer': message.text})
    await message.answer('Выберите раздел для вопроса.Укажите только <b>id</b> раздела.Вы\
   можете посмотреть список разделов командой /list_sections')
    await state.set_state(CreateQuestion.select_section)

@router.message(CreateQuestion.select_section, F.text)
async def cmd_select_section(message: Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    if not await session.get(Section, message.text):
        await message.answer('Раздела с указанным id не существует.Укажите id существующего раздела:')
        return
    question = Question(question=user_data['question'],
                       answer=user_data['answer'], section_id=message.text)
    session.add(question)
    await session.commit()
    await message.answer(f"Вопрос успешно создан")
    await state.clear()

@router.message(Command('list_questions'))
async def cmd_list_questions(message: Message, command: CommandObject, session: AsyncSession):
    msg = '<u>Список вопросов:</u>\n(В формате ID: вопрос - ответ)\n\n'
    if not command.args:
        await message.answer("Для того, чтобы получть список вопросов, необходимо указать id раздела")
        return
    current_section = await session.get(Section, command.args, options=[selectinload(Section.questions)])
    if not current_section:
        await message.answer('Секции с указаным id не существует')
    elif not current_section.questions:
        await message.answer(f'Для секции {current_section.title} не существует вопросов')
    else:
        for question in current_section.questions:
            msg += f"{question.id}: {question.question} - {question.answer}\n"
        await message.answer(msg)

@router.message(Command('delete_question'))
async def cmd_delete_question(message: Message, command: CommandObject, session: AsyncSession):
    question = await session.get(Question, command.args)
    if not question:
        await message.answer('Вопроса с указанным id не существует')
    else:
        await session.delete(question)
        await message.answer(f"Вопрос с id {command.args} успешно удалён")