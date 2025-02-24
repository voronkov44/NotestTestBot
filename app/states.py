from aiogram.fsm.state import State, StatesGroup

class Task(StatesGroup):
    name = State()
    text = State()
    action = State()  # Поле для хранения контекста (create или edit)