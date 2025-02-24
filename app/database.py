from __future__ import annotations
from aiomysql import Pool

import aiomysql
import logging
from typing import List, Optional, Any

pool: Pool | None = None  # Глобальный пул соединений


async def init_db():
    """Создание пула подключений к БД при запуске бота"""
    global pool
    try:
        logging.info("🔄 Инициализация пула подключений...")
        pool = await aiomysql.create_pool(
            host="",
            user="",
            password="",
            db="",
            minsize=1,
            maxsize=10,
            autocommit=True
        )
        logging.info("✅ Пул подключений к БД создан!")
        logging.info(f"Пул инициализирован: {pool}")
    except Exception as e:
        logging.error(f"Ошибка при инициализации пула подключений: {e}")
        raise e


async def close_db():
    """Закрытие пула подключений при завершении работы"""
    global pool
    if pool:
        try:
            pool.close()  # Используем await
            await pool.wait_closed()
            logging.info("🛑 Пул подключений к БД закрыт!")
        except Exception as e:
            logging.error(f"Ошибка при закрытии пула подключений: {e}")
    else:
        logging.error("⛔ Пул подключений не инициализирован, не удалось закрыть.")


async def get_db_connection():
    """Получаем соединение из пула с использованием контекстного менеджера"""
    global pool
    if not pool:
        logging.error("⛔ Пул подключений не инициализирован!")
        return None
    if not isinstance(pool, aiomysql.pool.Pool):  # Исправлено
        logging.error("⛔ pool был переопределен и не является объектом Pool!")
        return None
    try:
        logging.info(f"🔄 Пул подключений, текущее количество соединений: {pool.size} из {pool.maxsize}")  # Исправлено
        async with pool.acquire() as connection:
            return connection
    except Exception as e:
        logging.error(f"Ошибка при получении соединения из пула: {e}")
        return None


# Сохранение данных пользователя в базе данных
async def save_user_to_db(user_tg: int, username: str | None, first_name: str, last_name: str | None):
    connection = await get_db_connection()
    if not connection:
        logging.error("Не удалось подключиться к базе данных.")
        return

    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE user_tg = %s", (user_tg,))
            user = await cursor.fetchone()

            if user is None:
                sql = "INSERT INTO users (user_tg, username, first_name, last_name) VALUES (%s, %s, %s, %s)"
                values = (user_tg, username, first_name, last_name)
                await cursor.execute(sql, values)
                await connection.commit()
    except Exception as e:
        logging.error(f"Ошибка при сохранении пользователя в базе данных: {e}")


# Сохранение новой задачи в базу данных
async def save_task_to_db(task_name: str, task_text: str | None, user_tg: int):
    connection = await get_db_connection()
    if not connection:
        logging.error("Не удалось подключиться к базе данных.")
        return

    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE user_tg = %s", (user_tg,))
            user = await cursor.fetchone()

            if user:
                user_id = user[0]
            else:
                logging.error(f"Ошибка: пользователь с tg_id {user_tg} не найден!")
                return

            sql = "INSERT INTO tasks (user_id, task_name, task_text) VALUES (%s, %s, %s)"
            values = (user_id, task_name, task_text)
            await cursor.execute(sql, values)
            await connection.commit()
    except Exception as e:
        logging.error(f"Ошибка при сохранении задачи в базе данных: {e}")


# Изменение новой задачи в базу данных
async def update_task_in_db(task_id: int, task_name: str, task_text: str | None) -> bool:
    connection = await get_db_connection()
    if not connection:
        return False

    try:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE tasks SET task_name = %s, task_text = %s WHERE id = %s",
                (task_name, task_text, task_id)
            )
            await connection.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи {task_id}: {e}")
        return False


async def get_user_tasks(user_tg: int) -> Optional[List[dict]]:
    connection = await get_db_connection()
    if not connection:
        return None
    try:
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT id FROM users WHERE user_tg = %s", (user_tg,))
            user = await cursor.fetchone()
            if not user:
                return None
            user_id = user["id"]
            await cursor.execute("SELECT id, task_name FROM tasks WHERE user_id = %s AND is_done = 0", (user_id,))
            tasks = await cursor.fetchall()
        return tasks
    except Exception as e:
        logging.error(f"Ошибка при получении задач: {e}")
        return None


# Функция для получения выполненых задач пользователя из базы данных
async def get_user_tasks_completed(user_tg: int) -> Optional[List[dict]]:
    connection = await get_db_connection()
    if not connection:
        logging.error("Не удалось подключиться к базе данных.")
        return None

    try:
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT id FROM users WHERE user_tg = %s", (user_tg,))
            user = await cursor.fetchone()

            if not user:
                return None

            user_id = user["id"]

            await cursor.execute(
                "SELECT id, task_name FROM tasks WHERE user_id = %s AND is_done = 1",
                (user_id,)
            )
            tasks = await cursor.fetchall()

        return tasks
    except Exception as e:
        logging.error(f"Ошибка при получении задач пользователя с tg_id {user_tg}: {e}")
        return None


# Функция для получения данных задачи по ID
async def get_task_by_id(task_id: int) -> Any | None:
    connection = await get_db_connection()
    if not connection:
        logging.error("Не удалось подключиться к базе данных.")
        return None

    try:
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT task_name, task_text FROM tasks WHERE id = %s", (task_id,))
            task = await cursor.fetchone()

        return task
    except Exception as e:
        logging.error(f"Ошибка при получении задачи с id {task_id}: {e}")
        return None


#Функция, которая меняет таску с актуальной на выполненую, заменяет 0 на 1
async def mark_task_as_done(task_id: int) -> bool:
    connection = await get_db_connection()
    if not connection:
        return False
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE tasks SET is_done = 1 WHERE id = %s", (task_id,))
            await connection.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи {task_id}: {e}")
        return False


# Функция, которая удаляет таску в таблице tasks
async def delete_task_from_db(task_id: int) -> bool:
    connection = await get_db_connection()
    if not connection:
        return False

    try:
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            await connection.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка при удалении задачи {task_id}: {e}")
        return False


#Функция, которая меняет таску с выполненной на актуальную, заменяет 1 на 0
async def mark_task_as_actualize(task_id: int) -> bool:
    connection = await get_db_connection()
    if not connection:
        return False
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE tasks SET is_done = 0 WHERE id = %s", (task_id,))
            await connection.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи {task_id}: {e}")
        return False

########