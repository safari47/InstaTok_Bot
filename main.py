import logging
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from handlers.start import router as start_router
from config.config import bot, admins, dp, settings


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [BotCommand(command='start', description='Старт')]
    # Устанавливаем эти команды как дефолтные для всех пользователей    
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    # Устанавливаем командное меню    
    await set_commands()
    # Устанавливаем вебхук для приема сообщений через заданный URL
    await bot.set_webhook(f"{settings.BASE_URL}{settings.WEBHOOK_PATH}")
    # Отправляем сообщение админам о том, что бот был запущен
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    # Отправляем сообщение админам о том, что бот был остановлен
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления или сохраняем
    await bot.delete_webhook(drop_pending_updates=False)
    # Закрываем сессию бота, освобождая ресурсы    
    await bot.session.close()
    logger.error("Бот остановлен!")


# Основная функция, которая запускает приложение
def main() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(start_router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(start_bot)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(stop_bot)

    # Создаем веб-приложение на базе aiohttp
    app = web.Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,  # Передаем диспетчер
        bot=bot  # Передаем объект бота
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(app, host=settings.HOST, port=settings.PORT)

# Точка входа в программу
if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    main()  # Запускаем основную функцию