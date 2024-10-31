from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.kb import main_contact_kb
from utils.utils import download_instagram_post

router = Router()


# Функция для реагирования на команду /start
@router.message(CommandStart())
async def start(message: Message):
    telegram_id = message.from_user.id
    await message.answer("Выберите опцию:", reply_markup=main_contact_kb())


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


@router.message()
async def download_media(message: Message):
    input_url = message.text
    output_media = download_instagram_post(input_url)
    if isinstance(output_media, str):
        await message.answer(output_media)
    else:
        for type, url in output_media.items():
            if "Изображение" in type:
                await message.answer_photo(url)
            elif "Видео" in type:
                await message.answer_video(url)
