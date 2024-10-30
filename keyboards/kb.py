from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_contact_kb():
    # Создание кнопок
    buttons = [
        [KeyboardButton(text="💬 INFO")] 
    ]

    # Создание клавиатуры
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,   
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Введите URL поста",
    )
    return keyboard



# buttons = [
#         [
#             KeyboardButton(
#                 text="📷 INSTAGRAM",
#             ),
#             KeyboardButton(
#                 text="📺 INSTAGRAM",
#             ),
#         ],
#         [
#             KeyboardButton(
#                 text="📺 TIKTOK",
#             ),
#             KeyboardButton(
#                 text="💬 INFO",
#             ),
#         ],
#     ]
