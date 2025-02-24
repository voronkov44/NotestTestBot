import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers.router import router
from app.database import init_db, close_db

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def on_startup():
    """Функция, которая будет вызываться при запуске бота"""
    logging.info("🟢 Бот запускается...")
    await init_db()  # Инициализация пула подключений
    logging.info("✅ Пул подключений к БД инициализирован!")

async def on_shutdown():
    """Функция, которая будет вызываться при завершении работы бота"""
    logging.info("🔴 Бот выключается...")
    await close_db()  # Закрытие пула подключений
    logging.info("🛑 Пул подключений к БД закрыт!")

async def main():
    await on_startup()  # Инициализируем пул перед запуском бота
    dp.include_router(router)
    try:
        await dp.start_polling(bot)  # Запускаем polling, передав bot
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
    finally:
        await on_shutdown()  # Завершаем работу при любых ошибках

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования
    asyncio.run(main())  # Запускаем основной асинхронный цикл