from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, get_flowers_keyboard
from ..config.media import FLOWERS_PICTURES
import sqlite3
import os
from dotenv import load_dotenv
from ..database.models import create_flowers_table


def is_waiting_broadcast(handler):
    async def filter_func(message: types.Message, event_from_user):
        return handler._waiting_broadcast == event_from_user.id
    return filter_func

class AdminHandlers:
    def __init__(self, dp: Dispatcher):
        load_dotenv()
        self.admin_ids = os.getenv("ADMIN_IDS", "")
        self.admin_ids = [int(x) for x in self.admin_ids.split(",") if x.strip()]
        self._waiting_broadcast = None
        create_flowers_table()
        dp.message.register(self.admin_panel, Command("admin"))
        dp.message.register(
            self.broadcast_message,
            is_waiting_broadcast(self),
        )

    async def admin_panel(self, message: types.Message):        

        if message.from_user.id not in self.admin_ids:
            await message.answer("У вас нет доступа к админ-панели.")
            return

        await message.answer("Введите текст рассылки для всех пользователей:")

        self._waiting_broadcast = message.from_user.id

    async def broadcast_message(self, message: types.Message):
        broadcast_text = message.text

        # Получаем всех пользователей из базы данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        sent = 0
        for user_id in user_ids:
            try:
                await message.bot.send_message(user_id, broadcast_text)
                sent += 1
            except Exception:
                continue

        await message.answer(f"Рассылка завершена. Сообщение отправлено {sent} пользователям.")

        # Сброс состояния
        self._waiting_broadcast = None