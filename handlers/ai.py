from aiogram import Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from ..services.ai import AI_GPT
from ..config import get_base_keyboard
from ..database.models import MessageManager
from .admin import AdminStates

class AI_Handlers:  
    def __init__(self, dp: Dispatcher):
        self.gpt = AI_GPT()
        dp.message.register(
            self.fallback_handler,
            F.text,
            # ~Command(commands=["admin", "start", "help", "catalog", "order"]),
            # ~StateFilter(AdminStates.waiting_category_name),
            # ~StateFilter(AdminStates.waiting_flower_name),
            # ~StateFilter(AdminStates.waiting_flower_caption),
            # ~StateFilter(AdminStates.waiting_flower_photo),
            # ~StateFilter(AdminStates.waiting_flower_category),
        )

    async def fallback_handler(self, message: types.Message):
        if message.text and message.text.startswith('/'):
            return
            
        user_id = message.from_user.id
        thinking_msg = await message.answer("ChatGPT печатает...")

        try:
            await MessageManager.add_message(user_id, "user", message.text)
            history = await MessageManager.get_history(user_id, limit=10)
            response = self.gpt.ask_gpt(history)
            await MessageManager.add_message(user_id, "assistant", response)

            await thinking_msg.delete()
            await message.answer(response, reply_markup=get_base_keyboard())

        except Exception as e:
            await thinking_msg.delete()
            await message.answer(f"Произошла ошибка: {str(e)}")