from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states import Task
from app.database import get_task_by_id, mark_task_as_done, delete_task_from_db, update_task_in_db, \
    mark_task_as_actualize, get_user_tasks, get_user_tasks_completed
from app.keyboards import inline as kb_inline

router = Router()

@router.callback_query(F.data.startswith("completed_task_"))
async def show_completed_task_details(callback: CallbackQuery):
    completed_task_id = int(callback.data.split("_")[2])  # Используем индекс 2
    task = await get_task_by_id(completed_task_id)

    if not task:
        await callback.answer("Ошибка: Заметка не найдена!", show_alert=True)
        return

    task_text = task["task_text"] if task["task_text"] else "Вы ничего не ввели 🤷‍♀️"
    keyboard = kb_inline.get_completed_task_control_buttons(completed_task_id)

    await callback.message.edit_text(
        f"📌 <b>{task['task_name']}</b>\n\n{task_text}",
        parse_mode="HTML", reply_markup=keyboard
    )

@router.callback_query(F.data == "back_to_list_completed_task")
async def back_to_completed_task_list(callback: CallbackQuery):
    user_tg = callback.from_user.id
    tasks = await get_user_tasks_completed(user_tg)  # Используем get_user_tasks_completed

    if not tasks:
        await callback.message.edit_text("У вас пока нет выполненных заметок.")
        return

    await callback.message.edit_text("Ваши выполненные заметки:", reply_markup=kb_inline.completedTasks_keyboard(tasks))

@router.callback_query(F.data.startswith("actualize_"))
async def mark_task_actualize(callback: CallbackQuery):
    completed_task_id = int(callback.data.split("_")[1])
    success = await mark_task_as_actualize(completed_task_id)

    if success:
        await callback.answer("🔄 Задача снова актуальная!")
        user_tg = callback.from_user.id
        tasks = await get_user_tasks_completed(user_tg)  # Используем get_user_tasks_completed

        if not tasks:
            await callback.message.edit_text("🔄 Задача актуальна!\nУ вас больше нет выполненных заметок.")
        else:
            await callback.message.edit_text(
                "🔄 Задача актуальна!\nВот ваш обновленный список выполненных заметок:",
                reply_markup=kb_inline.completedTasks_keyboard(tasks)
            )
    else:
        await callback.answer("❌ Ошибка при обновлении задачи!", show_alert=True)

@router.callback_query(F.data.startswith("delete_actualize_"))
async def delete_actualize_task(callback: CallbackQuery):
    completed_task_id = int(callback.data.split("_")[2])
    success = await delete_task_from_db(completed_task_id)

    if success:
        await callback.answer("🗑 Задача удалена!")
        await callback.message.delete()
    else:
        await callback.answer("❌ Ошибка при удалении задачи!", show_alert=True)
        return

    user_tg = callback.from_user.id
    tasks = await get_user_tasks_completed(user_tg)  # Используем get_user_tasks_completed

    if not tasks:
        await callback.message.answer("🗑 Задача удалена!\nУ вас больше нет выполненных заметок.")
    else:
        await callback.message.answer("📋 Ваши выполненные заметки:", reply_markup=kb_inline.completedTasks_keyboard(tasks))


# Обработчик для задач
@router.callback_query(F.data.startswith("task_"))
async def show_task_details(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    task = await get_task_by_id(task_id)

    if not task:
        await callback.answer("Ошибка: Заметка не найдена!", show_alert=True)
        return

    task_text = task["task_text"] if task["task_text"] else "Вы ничего не ввели 🤷‍♀️"
    keyboard = kb_inline.get_task_control_buttons(task_id)

    await callback.message.edit_text(
        f"📌 <b>{task['task_name']}</b>\n\n{task_text}",
        parse_mode="HTML", reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("done_"))
async def mark_task_done(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    success = await mark_task_as_done(task_id)

    if success:
        await callback.answer("✅ Задача выполнена!")
        user_tg = callback.from_user.id
        tasks = await get_user_tasks(user_tg)

        if not tasks:
            await callback.message.edit_text("✅ Задача выполнена!\nУ вас больше нет активных заметок.")
        else:
            await callback.message.edit_text(
                "✅ Задача выполнена!\nВот ваш обновленный список заметок:",
                reply_markup=kb_inline.allTasks_keyboard(tasks)
            )
    else:
        await callback.answer("❌ Ошибка при обновлении задачи!", show_alert=True)

@router.callback_query(F.data.startswith("delete_"))
async def delete_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    success = await delete_task_from_db(task_id)

    if success:
        await callback.answer("🗑 Задача удалена!")
        await callback.message.delete()
    else:
        await callback.answer("❌ Ошибка при удалении задачи!", show_alert=True)
        return

    user_tg = callback.from_user.id
    tasks = await get_user_tasks(user_tg)

    if not tasks:
        await callback.message.answer("🗑 Задача удалена!\nУ вас больше нет активных заметок.")
    else:
        await callback.message.answer("📋 Ваши заметки:", reply_markup=kb_inline.allTasks_keyboard(tasks))

@router.callback_query(F.data == "back_to_list_task")
async def back_to_task_list(callback: CallbackQuery):
    user_tg = callback.from_user.id
    tasks = await get_user_tasks(user_tg)

    if not tasks:
        await callback.message.edit_text("У вас пока нет сохраненных заметок.")
        return

    await callback.message.edit_text("Ваши заметки:", reply_markup=kb_inline.allTasks_keyboard(tasks))

@router.callback_query(F.data.startswith("edit_"))
async def edit_task_callback(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    await state.update_data(task_id=task_id, action="edit")
    await state.set_state(Task.name)
    await callback.message.answer("✏️ Введите новое название заметки:")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()