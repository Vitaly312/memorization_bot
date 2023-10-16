from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def question_keyboard(sections: str):
    '''keyboard select sections'''
    builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=section, callback_data=section) for section in sections]
    builder.add(*buttons)
    return builder.as_markup()