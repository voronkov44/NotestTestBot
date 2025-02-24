from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import Task
from app.database import save_task_to_db, update_task_in_db, get_user_tasks
from app.keyboards import inline as kb_inline

router = Router()

MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 1000

@router.message(Task.name)
async def in_name_task(message: Message, state: FSMContext):
    title = message.text.strip()

    if len(title) > MAX_TITLE_LENGTH:
        await message.answer(f"❌ Название слишком длинное! Максимум {MAX_TITLE_LENGTH} символов.")
        return

    await state.update_data(name=title)
    await state.set_state(Task.text)

    data = await state.get_data()
    action = data.get("action")

    if action == "create":
        await message.answer("Введите описание заметки\n(Если не хотите писать описание - напишите NULL)")
    elif action == "edit":
        await message.answer("✏️ Введите новое описание заметки\n(Если не хотите писать описание - напишите NULL)")

@router.message(Task.text)
async def in_text_task(message: Message, state: FSMContext):
    text = message.text.strip()

    if text.lower() != "null" and len(text) > MAX_DESCRIPTION_LENGTH:
        await message.answer(f"❌ Описание слишком длинное! Максимум {MAX_DESCRIPTION_LENGTH} символов.")
        return

    task_text = None if text.lower() == "null" else text
    await state.update_data(text=task_text)

    data = await state.get_data()
    action = data.get("action")

    if action == "create":
        user_id = message.from_user.id
        await save_task_to_db(data["name"], data["text"], user_id)
        tasks = await get_user_tasks(user_id)

        if not tasks:
            await message.answer("✅ Заметка сохранена!\nУ вас больше нет активных заметок.")
        else:
            await message.answer(
                "✅ Заметка сохранена!\n📋 Ваши заметки:",
                reply_markup=kb_inline.allTasks_keyboard(tasks)
            )

    elif action == "edit":
        task_id = data.get("task_id")
        success = await update_task_in_db(task_id, data["name"], data["text"])

        if success:
            user_id = message.from_user.id
            tasks = await get_user_tasks(user_id)

            if not tasks:
                await message.answer("✅ Заметка успешно обновлена!\nУ вас больше нет активных заметок.")
            else:
                await message.answer(
                    "✅ Заметка успешно обновлена!\n📋 Ваши заметки:",
                    reply_markup=kb_inline.allTasks_keyboard(tasks)
                )
        else:
            await message.answer("❌ Ошибка при обновлении заметки.")

    await state.clear()