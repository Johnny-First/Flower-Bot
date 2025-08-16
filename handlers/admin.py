from aiogram.fsm.state import StatesGroup, State
from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, get_flowers_keyboard, get_my_keyboard
import sqlite3
import os
from dotenv import load_dotenv
from ..database.models import create_flowers_table, add_flower
from ..config import get_admin_keyboard

def is_waiting_broadcast(handler):
    async def filter_func(message: types.Message, event_from_user):
        return handler._waiting_broadcast == event_from_user.id
    return filter_func

class AdminStates(StatesGroup):
    pass

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
        dp.callback_query.register(self.admin_action_callback, F.data == "admin_interact_catalog" | F.data == "admin_mailing")
        dp.callback_query.register(self.interaction, F.data == "")

    async def admin_panel(self, message: types.Message):        
        if message.from_user.id not in self.admin_ids:
            await message.answer("У вас нет доступа к админ-панели.")
            return
        await message.answer(
            "Что бы вы хотели сделать, админ?",
            reply_markup=get_admin_keyboard()
        )
        self._waiting_broadcast = None  

    async def admin_action_callback(self, callback: types.CallbackQuery):
        if callback.from_user.id not in self.admin_ids:
            await callback.answer("Нет доступа", show_alert=True)
            return
        if callback.data == "admin_mailing":
            await callback.message.answer("Введите текст для рассылки:")
            self._waiting_broadcast = callback.from_user.id
            await callback.answer()
        elif callback.data == "admin_interact_catalog":
            await callback.message.edit_text("Опции:", reply_markup=
                                             get_my_keyboard("admin", {"Добавить категорию", "category_add"
                                            "Удалить категорию", "category_remove",
                                            "Добавить товар", "flower_add",
                                            "Удалить товар", "flower_remove"}))
            await callback.answer()
        else:
            await callback.answer("Неизвестное действие", show_alert=True)

    async def broadcast_message(self, message: types.Message):
        broadcast_text = message.text
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
        await message.answer(f"Рассылка завершена. Сообщение отправлено {sent} пользователям.", reply_markup=get_admin_keyboard())
        self._waiting_broadcast = None

    async def interaction(self, callback: types.CallbackQuery):
        pass

    async def add_flower():
        pass
    