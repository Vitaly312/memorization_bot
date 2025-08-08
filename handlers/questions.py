from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram import types
from keyboards.question import (
    question_keyboard,
    stop_survey_kb,
    rm_kb,
    QuestionSectionCallbackFactory,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from random import choice
from middlewares.authorization import CreateUserMiddleware
from service import views, questions as question_service, uow


router = Router()
router.message.middleware(CreateUserMiddleware())
router.callback_query.middleware(CreateUserMiddleware())


async def get_random_question(questions: dict[str, str]) -> tuple[str, str]:
    """Remove random question and answer from dict and return them"""
    question = choice(list(questions.keys()))
    return question, questions.pop(question)


class ExecutingSurvey(StatesGroup):
    wait_answer = State()


@router.message(Command("start_survey"))
async def select_section(message: Message):
    sections = await views.get_section_titles(uow=uow.SQLAlchemyUnitOfWork())
    if sections:
        await message.answer(
            "Выберите раздел", reply_markup=question_keyboard(sections)
        )
    else:
        await message.answer("На данный момент разделы не существуют")


@router.callback_query(QuestionSectionCallbackFactory.filter(), StateFilter(None))
async def handle_cb_section_selected(
    callback: types.CallbackQuery,
    callback_data: QuestionSectionCallbackFactory,
    state: FSMContext,
):
    questions = {
        question.question: question.answer
        for question in await views.get_section_questions_and_answers(
            uow=uow.SQLAlchemyUnitOfWork(), section_title=callback_data.section
        )
    }
    await callback.message.answer(f"Вы выбрали раздел {callback_data.section}")
    if not questions:
        await callback.message.answer("Для этого раздела нет вопросов")
        await callback.answer()
        return
    question, answer = await get_random_question(questions)
    await state.update_data(
        {
            "questions": questions,
            "current_answer": answer,
            "correct_answers_count": 0,
            "section": callback_data.section,
        }
    )
    await callback.message.answer(question, reply_markup=stop_survey_kb())
    await state.set_state(ExecutingSurvey.wait_answer)
    await callback.answer()


@router.message(ExecutingSurvey.wait_answer, F.text == "Завершить опрос")
async def exit_survey(message: Message, state: FSMContext):
    await message.answer("Вы завершили опрос")
    await handle_survey_ending(message, state)


@router.message(ExecutingSurvey.wait_answer, F.text)
async def get_next_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower() == user_data["current_answer"].lower():
        await state.update_data(
            {"correct_answers_count": user_data["correct_answers_count"] + 1}
        )
        await message.answer("Правильно")
    else:
        await message.answer(
            f"Неправильно.Правильный ответ: {user_data['current_answer'].lower()}"
        )
    questions = user_data["questions"]
    if questions:
        question, answer = await get_random_question(user_data["questions"])
        await state.update_data({"questions": questions, "current_answer": answer})
        await message.answer(question)
    else:
        await handle_survey_ending(message, state)


async def handle_survey_ending(message: Message, state: FSMContext):
    user_data = await state.get_data()
    result = await question_service.save_survey_result(
        uow=uow.SQLAlchemyUnitOfWork(),
        section_title=user_data["section"],
        correct_answers_count=user_data["correct_answers_count"],
        user_tg_id=message.from_user.id,
    )
    await message.answer(f"Правильных ответов: {result.result}", reply_markup=rm_kb())
    await state.clear()


def _format_stat_value(value: float | None) -> str:
    if value is None:
        return "Нет данных"
    return f"{value:.1f}%"


@router.message(Command("info"))
async def cmd_get_info(message: Message):
    stat = await views.get_stat(
        uow=uow.SQLAlchemyUnitOfWork(), user_tg_id=message.from_user.id
    )
    if not stat:
        await message.answer("Нет данных")
        return
    msg = "<b>Результаты по всем разделам(среднее значение):</b>\n\n"
    for section_stat in stat:
        msg += f"<u>{section_stat.section_title}</u>\n"
        msg += f"\t\t\tЗа текущий день: {_format_stat_value(section_stat.day_result)}\n"
        msg += (
            f"\t\t\tЗа все время: {_format_stat_value(section_stat.total_result)}\n\n"
        )
    await message.answer(msg)
