from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import Task
from app.database import save_user_to_db, get_user_tasks, get_user_tasks_completed
from app.keyboards import inline as kb_inline

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}!\nЭто бот с задачами')
    await save_user_to_db(
        user_tg=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

# /newTask
@router.message(Command('newtask'))
async def in_name_task(message: Message, state: FSMContext):
    await state.update_data(action="create")
    await state.set_state(Task.name)
    await message.answer("Введите название заметки")

# /allTask
@router.message(Command('alltask'))
async def show_tasks(message: Message):
    user_tg = message.chat.id
    tasks = await get_user_tasks(user_tg)

    if not tasks:
        await message.answer("У вас пока нет сохраненных заметок.")
        return

    await message.answer("Ваши заметки:", reply_markup=kb_inline.allTasks_keyboard(tasks))

# /completedTask
@router.message(Command('completedtask'))
async def show_completed_tasks(message: Message):
    user_tg = message.chat.id
    tasks = await get_user_tasks_completed(user_tg)

    if not tasks:
        await message.answer("У вас пока нет выполненных заметок.")
        return

    await message.answer("Ваши выполненные заметки:", reply_markup=kb_inline.completedTasks_keyboard(tasks))