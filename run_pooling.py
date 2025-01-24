import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from handlers.start import router as start_router
from config.config import bot, dp,settings
from utils.db import initialize_database
import logging

# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command="start", description="Старт")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()

    await initialize_database()
    await bot.send_message(settings.ADMIN_IDS, f"Я запущен🥳.")

    logger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    await bot.send_message(settings.ADMIN_IDS, f"Бот остановлен. За что?😔")
    logger.error("Бот остановлен!")


async def main():
    dp.include_router(start_router)

    # регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    # запуск бота в режиме long polling при запуске бот очищает все обновления, которые были за его моменты бездействия
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(
        __name__
    )  # Создаем логгер для использования в других частях программы
    asyncio.run(main())
