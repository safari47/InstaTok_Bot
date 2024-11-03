import aiosqlite


async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("bot.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT
            )
        """)
        # Сохраняем изменения
        await db.commit()


async def add_user(telegram_id: int, username: str, first_name: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id, username, first_name))
        await db.commit()


# Функция для получения всех пользователей в виде списка словарей
async def get_all_users():
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()

        # Преобразуем результаты в список словарей
        users = [
            {
                "telegram_id": row[0],
                "username": row[1],
                "first_name": row[2]
            }
            for row in rows
        ]
        return users


# Функция для получения данных о пользователе по telegram_id в виде словаря
async def get_user_by_id(telegram_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        # Преобразуем результат в словарь
        user = {
            "telegram_id": row[0],
            "username": row[1],
            "first_name": row[2]
        }
        return user