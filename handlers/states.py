from aiogram.fsm.state import StatesGroup, State

class ExecutingSurvey(StatesGroup):
    wait_answer = State()

class CreateQuestion(StatesGroup):
    create_question = State()
    create_answer = State()
    select_section = State()