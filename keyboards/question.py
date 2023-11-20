from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def question_keyboard(sections: list[str]):
    '''keyboard select sections'''
    builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=section, callback_data=section) for section in sections]
    builder.add(*buttons)
    builder.adjust(3)
    return builder.as_markup()

def stop_survey_kb():
    exit_btn = [KeyboardButton(text='Завершить опрос')]
    kb = ReplyKeyboardMarkup(keyboard=[exit_btn], resize_keyboard=True)
    return kb

def rm_kb():
    return ReplyKeyboardRemove()