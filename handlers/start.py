from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message,FSInputFile
from keyboards.kb import main_contact_kb
from aiogram.utils.markdown import hlink
from utils.instagram.instagram import download_instagram_post
from utils.db import get_user_by_id, add_user
from utils.tiktok.get_content import get_content
from utils.tiktok.get_video_detail import get_video_detail
from utils.tiktok.musicaldown import musicaldown
import pathlib
from loguru import logger

cwd = pathlib.Path(__file__).parent.parent
router = Router()

# Функция для реагирования на команду /start
@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.first_name
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)
    if user_data is None:
        await add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    welcome_text = (
        f"Привет, {username}! Я готов к работе. 🔗\n\n"
        f"Просто отправьте мне ссылку, а я всё сделаю. 📸🎥"
    )
    await message.answer(welcome_text, reply_markup=main_contact_kb())


@router.message(F.text == "💬 INFO")
async def bot_info(message: Message):
    await message.answer(
        f"🔥 Информация о боте 🔥\n"
        f"\n"
        f"👤 Владелец бота: Artem Kozlov\n"
        f"📬 Контакт владельца: @safarik47\n"
        f"\n"
        f"💵 Вы можете всегда меня отблагодарить:\n"
        f"\n"
        f"{hlink('Подкинуть копеечку 😇','https://www.tbank.ru/cf/AGhwjuw96bl')}\n"
        f"\n"
        f"💡 Основные функции:\n"
        f"🔍 Загрузка рилсов, IGTV видео Instagram\n"
        f"🔍 Загрузка фото из постов Instagram\n"
        f"🔍 Загрузка видео TikTok\n"
        f"\n"
        f"💡 Преимущества:\n"
        f"💨 Быстрота и эффективность\n"
        f"💵 Не требует подписок на множество каналов для использования\n",
        disable_web_page_preview=True
    )



instagram = [F.text.contains("instagram.com")]
@router.message(*instagram)
async def download_media(message: Message):
    wait_message = await message.answer(
        "Я уже начал скачивать видео 📹\nПодожди одну секундочку ⏳"
    )
    input_url = message.text
    try:
        output_media = download_instagram_post(input_url)
        
        await wait_message.delete()
        
        for media_type, url in output_media.items():
            try:
                if "Изображение" in media_type:
                    await message.answer_photo(url)
                elif "Видео" in media_type:
                    await message.answer_video(url)
            except Exception as e:
                logger.error(f"Ошибка {str(e)} при выгрузке URL: {input_url}")
                await message.answer(f"Извините, произошла ошибка при отправке медиа.\nПрисылайте другие ссылки.")
    except Exception as e:
        await wait_message.delete()  
        logger.error(f"Произошла ошибка при скачивании: {str(e)} URL: {input_url}")
        await message.reply(f"Произошла непредвиденная ошибка при скачивании поста.\nПожалуйста, попробуйте позже.")


tiktok = [F.text.contains("tiktok.com")]
@router.message(*tiktok)
async def download_tiktok(message: Message):
    output = None  # Инициализировать переменную output
    try:
        wait_message = await message.answer(
            "Я уже начал скачивать видео 📹\nПодожди одну секундочку ⏳"
        )

        input_url = message.text
        video_id, video_url, cookies = (await get_video_detail(input_url))

        if video_id is None:
            await message.answer(
                "Видео TikTok, которое вы хотите загрузить, не существует, возможно, оно удалено или является приватным видео."
            )
            return  # Завершить выполнение функции, если видео не найдено

        output_directory = cwd / "video_upload"
        output = output_directory / f"{video_id}.mp4"

        if video_url is None or len(video_url) <= 0:
            await musicaldown(url=input_url, output=output)
        else:
            await get_content(url=video_url, output=output, cookies=cookies)

        await wait_message.delete()  # Удалить сообщение о загрузке

        video = FSInputFile(output)
        await message.answer_video(video=video)

    except Exception as e:
        logger.error(f"Ошибка при загрузке видео TikTok: {str(e)} URL: {input_url}")
        await message.answer(
            f"Произошла ошибка при загрузке видео.\n Пожалуйста, попробуйте еще раз позже.")
    finally:
        # Проверяем, существует ли файл, перед удалением
        if output is not None and output.exists():
            output.unlink()


@router.message()
async def download_media(message: Message):
    await message.answer(
        f"Вы прислали странную ссылочку 📝\n"
        f"Незнаю даже, что с ней сделать 😰\n"
        f"Проверьте правильность 🔍 или \n"
        f"напишите мне @safarik47 🆘"
    )
