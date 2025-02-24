from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заметки')],
    [KeyboardButton(text='Корзина'), KeyboardButton(text='Контакты')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

notes = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Новая заметка')],
    [KeyboardButton(text='Удалить заметку')]
], resize_keyboard=True, input_field_placeholder='Выберите нужный пункт. . .')