from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import types
from database.models import User, Section, Result, Question
from database.connect import get_conn
from keyboards.question import question_keyboard, stop_survey_kb, rm_kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from random import choice
from middlewares.authorization import AuthorizeMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import func 
from datetime import datetime, timedelta


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())

def section_is_aviable(section_title):
    with get_conn() as session:
        sections = [s.title for s in session.query(Section).all()]
    return section_title in sections

async def get_random_question(questions):
    '''Remove random question and answer from dict and return them'''
    question = choice(list(questions.keys())) 
    return question, questions.pop(question)

class ExecutingSurvey(StatesGroup):
    wait_answer = State()

@router.message(Command('start_survey'))
async def start_survey(message: Message, session: Session):
    sections = [s.title for s in session.query(Section).all()]
    if sections:
        await message.answer("Выберите раздел", reply_markup=question_keyboard(sections))
    else:
        await message.answer("На данный момент разделы не существуют")

@router.callback_query(lambda cb: section_is_aviable(cb.data))
async def start_survey(callback: types.CallbackQuery, state: FSMContext, session: Session):
    current_state = await state.get_state()
    if current_state in ExecutingSurvey:
        await callback.message.answer('Для того, чтобы начать новый опрос, \
сначала завершите уже запущенный опрос')
        await callback.answer()
        return
    section = session.query(Section).filter(Section.title==callback.data).first()
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
async def exit_survey(message: Message, state: FSMContext, user: User, session: Session):
    user_data = await state.get_data()
    current_section = session.query(Section).filter(Section.title == user_data['section']).first()
    count_ans = len(current_section.questions) - len(user_data['questions']) - 1
    right_ans = int(user_data['true_answer'])
    result = right_ans / (count_ans or 1) * 100
    session.add(Result(result=result, user=user, section=current_section))
    await state.clear()
    await message.answer(f'Вы заверили опрос. Правильных ответов: {right_ans}/{count_ans}', reply_markup=rm_kb())



@router.message(ExecutingSurvey.wait_answer, F.text)
async def get_next_question(message: Message, state: FSMContext, user: User, session: Session):
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
        user_data = await state.get_data()
        current_section = session.query(Section).filter(Section.title == user_data['section']).first()
        all_ans = len(current_section.questions)
        right_ans = user_data['true_answer']        
        await message.answer(f"Правильных ответов: {right_ans}/{all_ans}", reply_markup=rm_kb())
        result = right_ans / all_ans * 100
        current_result = Result(result=result, user=user, section=current_section)
        session.add(current_result)
        await state.clear()

@router.message(Command('info'))
async def cmd_get_info(message: Message, user: User, session: Session):
    data = {}
    yesterday = datetime.now() - timedelta(days=1)
    for section in session.query(Section).all():
        total_result = session.query(func.avg(Result.result)).filter(Result.user==user,
                                                               Result.section==section).first()[0]
        result_for_day = session.query(func.avg(Result.result)).filter(Result.user==user,
                                                               Result.section==section,
                                                               Result.created_on > yesterday).first()[0]
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