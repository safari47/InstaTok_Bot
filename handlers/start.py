from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from keyboards.kb import main_contact_kb
from utils.instagram.instagrapi import download_instagram
from utils.db import get_user_by_id, add_user
from utils.tiktok.get_content import get_content
from utils.tiktok.get_video_detail import get_video_detail
import pathlib
from loguru import logger
from config.static import en, ru
from utils.tiktok.tiktok_api import get_response
from config.config import cl
from aiogram.types import InputMediaPhoto, InputMediaVideo
cwd = pathlib.Path(__file__).parent.parent
router = Router()


# Функция для реагирования на команду /start
@router.message(CommandStart())
async def start(message: Message):
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)

    if user_data is None:
        await add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )


    # Определяем язык пользователя (по умолчанию английский)
    user_language = "ru" if message.from_user.language_code == "ru" else "en"

    # Получаем текст приветствия и подставляем имя пользователя
    welcome_text = ru["welcome_text"] if user_language == "ru" else en["welcome_text"]
    welcome_text = welcome_text.format(username=message.from_user.username)

    await message.answer(welcome_text, reply_markup=main_contact_kb())


@router.message(F.text == "💬 INFO")
async def bot_info(message: Message):
    # Определяем язык пользователя (по умолчанию английский)
    language_code = "ru" if message.from_user.language_code == "ru" else "en"

    # Определяем текст для ответа
    response_text = ru["info"] if language_code == "ru" else en["info"]

    await message.answer(
        response_text.format(
            donate_url="https://www.tbank.ru/cf/AGhwjuw96bl"
        ),  # Добавляем ссылку на донат
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )


@router.message(F.text.regexp(r"(https?://(www\.)?instagram\.com/\S+)"))
async def download_media(message: Message):
    # Определяем язык пользователя (по умолчанию английский)
    language_code = "ru" if message.from_user.language_code == "ru" else "en"
    messages = ru["messages"] if language_code == "ru" else en["messages"]

    wait_message = await message.answer(messages["wait_message"])
    input_url = message.text
    try:
        output_media = await cl.download_instagram(post_url=input_url)

        await wait_message.delete()

        for media_type, url in output_media.items():
            try:
                if "Изображение" in media_type:
                    await message.answer_photo(url)
                elif "Видео" in media_type:
                    await message.answer_video(url)
            except Exception as e:
                logger.error(f"Ошибка: {str(e)} при выгрузке URL: {input_url}")
                await message.answer(messages["send_image_error"])
        else:
            logger.info(
                f"ID: {message.from_user.id}, Имя: {message.from_user.username} — успешно получил результат для Instagram."
            )
    except Exception as e:
        await wait_message.delete()
        logger.error(f"Произошла ошибка при скачивании: {str(e)} URL: {input_url}")
        await message.reply(messages["download_error"])


@router.message(F.text.regexp(r"(https?://(www\.|vm\.|vt\.|vn\.)?tiktok\.com/\S+)"))
async def download_tiktok(message: Message):
    # Определяем язык сообщения
    if message.from_user.language_code.startswith("ru"):
        messages = ru["messages"]
    else:
        messages = en["messages"]
    
    try:
        wait_message = await message.answer(messages["wait_message"])
        # Пробуем получить видео через get_response
        video = await get_response(message.text)
        await wait_message.delete()
        await message.answer_video(video)
        
        # Логируем успешное получение результата через get_response
        logger.info(
            f"ID: {message.from_user.id}, Имя: @{message.from_user.username} — успешно получил результат для TikTok через get_response."
        )
    except Exception as e:
        # Обработка ошибок, если get_response не удалось
        logger.error(f"Ошибка в get_response для ID: {message.from_user.id}, Имя: @{message.from_user.username}, Ошибка: {str(e)}")

        output = None  # Инициализировать переменную output
        try:
            wait_message = await message.answer(messages["wait_message"])

            input_url = message.text
            video_id, video_url, cookies = await get_video_detail(input_url)
            
            # Логирования получения детальной информации о видео
            if video_id is None:
                logger.warning(f"Не удалось найти видео ID для URL: {input_url}")
                await wait_message.delete()
                await message.answer(messages["tiktok_not_exist"])
                return  # Завершить выполнение функции, если видео не найдено

            output_directory = cwd / "video_upload"
            output = output_directory / f"{video_id}.mp4"

            await get_content(url=video_url, output=output, cookies=cookies)
            method_used = "get_content"

            await wait_message.delete()  # Удалить сообщение о загрузке

            video = FSInputFile(output)
            await message.answer_video(video=video)

            # Логируем успешное получение результата со способом
            logger.info(
                f"ID: {message.from_user.id}, Имя: @{message.from_user.username} — успешно получил результат для TikTok через {method_used}."
            )
        except Exception as e:
            # Логируем ошибки при загрузке видео
            logger.error(f"Ошибка при загрузке видео TikTok для ID: {message.from_user.id}, Имя: @{message.from_user.username}, Ошибка: {str(e)}, URL: {input_url}")
            await message.answer(messages["tiktok_download_error"])
        finally:
            # Проверяем, существует ли файл, перед удалением
            if output is not None and output.exists():
                output.unlink()




@router.message()
async def download_media(message: Message):
    # Определяем язык пользователя (по умолчанию английский)
    language_code = "ru" if message.from_user.language_code == "ru" else "en"
    messages = ru["messages"] if language_code == "ru" else en["messages"]

    await message.answer(messages["weird_link_message"])
