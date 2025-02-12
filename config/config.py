import os
from loguru import logger
from typing import List
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict
import instaloader
from instagrapi import Client

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: int
    HOST: str
    PORT: int
    BASE_URL: str
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    
    # Определение пути вебхука после объявления всех переменных
    @property
    def WEBHOOK_PATH(self):
        return f'/{self.BOT_TOKEN}'

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

# Получаем параметры для загрузки переменных среды
settings = Settings()

# Инициализируем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
# L=instaloader.Instaloader()

# Инициализация клиента и загрузка настроек
cl = Client()
cl.load_settings("insta_session.json")

# Авторизация (используется сохранённая сессия)
cl.login("antonio_frankis", "19081997.Safari.")
cl.get_timeline_feed()  # проверка сессии

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)
