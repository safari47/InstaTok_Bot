from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.kb import main_contact_kb
from utils.utils import download_instagram_post, download_tiktok_video

router = Router()


# Функция для реагирования на команду /start
@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.first_name
    welcome_text = (
        f"Привет, {username}! Я готов к работе. 🔗\n\n"
        f"Просто отправьте мне ссылку, а я всё сделаю. 📸🎥"
    )
    await message.answer(welcome_text, reply_markup=main_contact_kb())


@router.message(F.text == "💬 INFO")
async def bot_info(message: Message):
    owner_name = "Artem Kozlov"
    owner_contact = "@safarik47"
    stack = "Python, aiogram, TikTokApi, instaloader"
    bot_purpose = "Загрузка фото, видео из Instagram, TikTok"
    features = [
        "🔍 Загрузка рилсов, IGTV видео Instagram",
        "🔍 Загрузка фото из постов Instagram",
        "🔍 Загрузка видео TikTok",
    ]

    features_formatted = "\n".join(features)
    await message.answer(
        f"🔥 Информация о боте 🔥\n"
        f"\n"
        f"👤 Владелец бота: {owner_name}\n"
        f"📬 Контакт владельца: {owner_contact}\n"
        f"\n"
        f"🔧 Стек технологий: {stack}\n"
        f"📌 Назначение бота: {bot_purpose}\n"
        f"\n"
        f"💡 Основные функции:\n"
        f"{features_formatted}\n"
        f"\n"
    )


instagram = [F.text.contains("instagram.com")]


@router.message(*instagram)
async def download_media(message: Message):
    wait_message = await message.answer(
        f"Я уже начал скачивать видео 📹\n" f"подожди одну секундочку ⏳"
    )
    input_url = message.text
    output_media = download_instagram_post(input_url)
    await wait_message.delete()
    if isinstance(output_media, str):
        await message.answer(output_media)
    else:
        for type, url in output_media.items():
            if "Изображение" in type:
                await message.answer_photo(url)
            elif "Видео" in type:
                await message.answer_video(url)


tiktok = [F.text.contains("tiktok.com")]


@router.message(*tiktok)
async def download_tiktok(message: Message):
    wait_message = await message.answer(
        f"Я уже начал скачивать видео 📹\n" f"подожди одну секундочку ⏳"
    )
    input_url = message.text
    output_media = download_tiktok_video(input_url)
    await wait_message.delete()
    await message.answer_video(output_media)


@router.message()
async def download_media(message: Message):
    await message.answer(
        f"Вы прислали странную ссылочку 📝\n"
        f"Незнаю даже, что с ней сделать 😰\n"
        f"Проверьте правильность 🔍 или \n"
        f"напишите мне @safarik47 🆘"
    )
