from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Функция, которая возвращает inline клавиатуру allTasks
def get_task_control_buttons(task_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_{task_id}"),
            InlineKeyboardButton(text="✅ Выполнить", callback_data=f"done_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}"),
            InlineKeyboardButton(text="🔔 Уведомление", callback_data=f"notify_{task_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_list_task")
        ]
    ])
    return keyboard

# Функция, которая возвращает inline клавиатуру completedTask
def get_completed_task_control_buttons(completed_task_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Актуализировать", callback_data=f"actualize_{completed_task_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_actualize_{completed_task_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_list_completed_task")
        ]
    ])
    return keyboard


def allTasks_keyboard(tasks) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for task in tasks:
        builder.button(
            text=task["task_name"],  # Название заметки
            callback_data=f"task_{task['id']}"  # Callback с ID задачи
        )

    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()

def completedTasks_keyboard(completed_tasks) -> InlineKeyboardMarkup:
    completed_builder = InlineKeyboardBuilder()

    for task in completed_tasks:
        completed_builder.button(
            text=task["task_name"],
            callback_data=f"completed_task_{task['id']}"  # Уникальный callback_data
        )

    completed_builder.adjust(1)
    return completed_builder.as_markup()