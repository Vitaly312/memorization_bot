from aiogram import Router, F, html
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from handlers.states import CreateQuestion
from aiogram.fsm.context import FSMContext
from middlewares.authorization import setup_middlewares
from middlewares.admin import IsAdminMiddleware
from service.uow import SQLAlchemyUnitOfWork
from service import use_cases, views, exceptions


router = Router()
setup_middlewares(router)
router.message.middleware(IsAdminMiddleware())


@router.message(Command("list_sections"))
async def cmd_list_sections(message: Message, uow: SQLAlchemyUnitOfWork):
    sections = await views.get_section_titles_and_ids(uow=uow)
    if not sections:
        await message.answer("На данный момент разделы не существуют")
    else:
        msg = "<u>Список разделов:</u>\n(В формате ID - название раздела)\n\n"
        for section in sections:
            msg += f"{section.id} - {section.title}\n"
        await message.answer(msg, parse_mode="HTML")


@router.message(Command("create_section"))
async def cmd_create_section(message: Message, command: CommandObject, uow: SQLAlchemyUnitOfWork):
    if not command.args:
        await message.answer("Необходимо указать название раздела")
        return
    try:
        await use_cases.create_section(uow=uow, title=command.args)
        await message.answer(f"Раздел с названием {command.args} успешно создан")
    except exceptions.SectionAlreadyExistsException:
        await message.answer(
            "Раздел с таким названием уже существует. Выберите другое название раздела"
        )


@router.message(Command("delete_section"))
async def cmd_delete_section(message: Message, command: CommandObject, uow: SQLAlchemyUnitOfWork):
    try:
        await use_cases.delete_section(uow, command.args)
        await message.answer(f"Раздел с названием {command.args} успешно удалён")
    except exceptions.SectionNotFoundException:
        await message.answer("Раздела с таким названием не существует")


@router.message(Command("create_question"))
async def cmd_new_question(message: Message, state: FSMContext):
    await message.answer("Напишите вопрос")
    await state.set_state(CreateQuestion.create_question)


@router.message(CreateQuestion.create_question, F.text)
async def cmd_create_answer(message: Message, state: FSMContext):
    await state.update_data({"question": message.text})
    await message.answer("Напишите ответ к вопросу")
    await state.set_state(CreateQuestion.create_answer)


@router.message(CreateQuestion.create_answer, F.text)
async def cmd_create_question(message: Message, state: FSMContext):
    await state.update_data({"answer": message.text})
    await message.answer(
        "Выберите раздел для вопроса.Укажите только <b>id</b> раздела.Вы\
   можете посмотреть список разделов командой /list_sections"
    )
    await state.set_state(CreateQuestion.select_section)


@router.message(CreateQuestion.select_section, F.text)
async def cmd_select_section(message: Message, state: FSMContext, uow: SQLAlchemyUnitOfWork):
    user_data = await state.get_data()
    try:
        await use_cases.create_question(
            uow,
            user_data["question"],
            user_data["answer"],
            int(message.text) if message.text.isdigit() else None,
        )
    except exceptions.SectionNotFoundException:
        await message.answer(
            "Раздела с указанным id не существует.Укажите id существующего раздела:"
        )
        return
    await message.answer("Вопрос успешно создан")
    await state.clear()


@router.message(Command("list_questions"))
async def cmd_list_questions(message: Message, command: CommandObject, uow: SQLAlchemyUnitOfWork):
    try:
        section_id = int(command.args or '')
    except ValueError:
        await message.answer("Необходимо указать id раздела")
        return
    questions = await views.get_questions_for_section(
        uow, section_id
    )
    if not questions:
        await message.answer(f"Для секции {command.args} не существует вопросов")
    else:
        msg = "<u>Список вопросов:</u>\n(В формате ID: вопрос - ответ)\n\n"
        for question in questions:
            msg += f"{question.id}: {html.quote(question.question)} - {html.quote(question.answer)}\n"
        await message.answer(msg)


@router.message(Command("delete_question"))
async def cmd_delete_question(message: Message, command: CommandObject, uow: SQLAlchemyUnitOfWork):
    try:
        await use_cases.delete_question(uow, int(command.args or ''))
        await message.answer(f"Вопрос с id {command.args} успешно удалён")
    except exceptions.QuestionNotFoundException:
        await message.answer("Вопроса с указанным id не существует")
