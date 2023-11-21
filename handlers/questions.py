from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import types
from database.models import User, Section, Result, Question
from keyboards.question import question_keyboard, stop_survey_kb, rm_kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from random import choice
from middlewares.authorization import AuthorizeMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func 
from datetime import datetime, timedelta
from filters.section_filters import SectionExistFilter
from sqlalchemy.orm import selectinload
from functools import reduce


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

async def get_random_question(questions):
    '''Remove random question and answer from dict and return them'''
    question = choice(list(questions.keys())) 
    return question, questions.pop(question)

class ExecutingSurvey(StatesGroup):
    wait_answer = State()

@router.message(Command('start_survey'))
async def start_survey(message: Message, session: AsyncSession):
    result = await session.execute(select(Section.title))
    sections = [data[0] for data in result]
    if sections:
        await message.answer("Выберите раздел", reply_markup=question_keyboard(sections))
    else:
        await message.answer("На данный момент разделы не существуют")

@router.callback_query(SectionExistFilter())
async def start_survey(callback: types.CallbackQuery,
                      state: FSMContext,
                      session: AsyncSession):
    current_state = await state.get_state()
    if current_state in ExecutingSurvey:
        await callback.message.answer('Для того, чтобы начать новый опрос, \
сначала завершите уже запущенный опрос')
        await callback.answer()
        return
    result = await session.execute(select(Section)
                                   .where(Section.title==callback.data)
                                   .options(selectinload(Section.questions)))
    section = result.scalar()
    questions = {question.question: question.answer for question in section.questions}
    await callback.message.answer(f"Вы выбрали раздел {section}")
    if not questions:
        await callback.message.answer("Для этого раздела нет вопросов")
        await callback.answer()
        return
    question, answer = await get_random_question(questions)
    await state.update_data({'questions': questions, 
                             'answer': answer, 'true_answer': 0,
                             'section': section.title})
    await callback.message.answer(question, reply_markup=stop_survey_kb())
    await state.set_state(ExecutingSurvey.wait_answer)
    await callback.answer()


@router.message(ExecutingSurvey.wait_answer, F.text == 'Завершить опрос')
async def exit_survey(message: Message, state: FSMContext, user: User, session: AsyncSession):
    await message.answer("Вы завершили опрос")
    await save_survey_result(message, user, session, state)


@router.message(ExecutingSurvey.wait_answer, F.text)
async def get_next_question(message: Message, state: FSMContext, user: User, session: AsyncSession):
    user_data = await state.get_data()
    if message.text == user_data['answer']:
        new_true_answer = user_data['true_answer'] + 1
        await state.update_data({'true_answer': new_true_answer})
        await message.answer('Правильно')
    else:
        await message.answer(f'Неправильно.Правильный ответ: {user_data["answer"]}')
    questions = user_data['questions']
    if questions:
            question, answer = await get_random_question(user_data['questions'])
            await state.update_data({'questions': questions, 'answer': answer})
            await message.answer(question)
    else:
        await save_survey_result(message, user, session, state)

async def save_survey_result(message: Message, user: User, session: AsyncSession, state: FSMContext):
    '''save results executing survey by user'''
    user_data = await state.get_data()
    result = await session.execute(select(Section).where(Section.title == user_data['section']).options(
        selectinload(Section.questions)
        ))
    section = result.scalar()
    if len(user_data.get('questions', ())):
        all_ans = len(section.questions) - len(user_data.get('questions', ())) - 1
    else:
        all_ans = len(section.questions)
    right_ans = user_data['true_answer']
    await message.answer(f"Правильных ответов: {right_ans}/{all_ans}", reply_markup=rm_kb())
    result = right_ans / (all_ans or 1) * 100
    current_result = Result(result=result, user=user, section=section)
    session.add(current_result)
    await state.clear()

@router.message(Command('info'))
async def cmd_get_info(message: Message, user: User, session: AsyncSession):
    data = {}
    yesterday = datetime.now() - timedelta(days=1)
    result = await session.execute(select(Section))
    for section in result.scalars():
        query_for_day = select(func.avg(Result.result)).filter(Result.user==user,
                                                               Result.section==section,
                                                               Result.created_on > yesterday)
        query_total = select(func.avg(Result.result)).filter(Result.user==user,
                                                               Result.section==section)
        result_for_day = (await session.execute(query_for_day)).first()[0]
        total_result = (await session.execute(query_total)).first()[0]
        total_res = []
        for result in (result_for_day, total_result):
            total_res.append(str(round(result, 1)) + '%' if result is not None else 'Нет данных')
        data[section.title] = total_res
            
    msg = '<b>Результаты по всем разделам(среднее значение):</b>\n\n'
    for section_title, (result, total_result) in data.items():
        msg += f"<u>{section_title}</u>\n"
        msg += f"\t\t\tЗа текущий день: {result}\n"
        msg += f"\t\t\tЗа все время: {total_result}\n\n"
    await message.answer(msg)