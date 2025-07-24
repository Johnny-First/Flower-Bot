from aiogram import Dispatcher, types
from ..services.ai import AI_GPT
from ..config import get_base_keyboard
from ..database.models import add_message, get_history, create_messages_table

class AI_Handlers:
    def __init__(self, dp: Dispatcher):
        create_messages_table()  # Создаём таблицу сообщений при запуске
        self.gpt = AI_GPT()
        dp.message.register(
            self.fallback_handler,
            flags={"run_last": True}
        )

    async def fallback_handler(self, message: types.Message):
        user_id = message.from_user.id
        thinking_msg = await message.answer("ChatGPT печатает...")

        # Сохраняем сообщение пользователя в историю
        add_message(user_id, "user", message.text)
        # Получаем последние 10 сообщений для контекста
        history = get_history(user_id, limit=10)

        try:
            # Передаём историю в ask_gpt (ожидается, что ask_gpt принимает список сообщений)
            response = self.gpt.ask_gpt(history)
            # Сохраняем ответ ассистента в историю
            add_message(user_id, "assistant", response)

            await thinking_msg.delete()
            await message.answer(response, reply_markup=get_base_keyboard())

        except Exception as e:
            await thinking_msg.delete()
            await message.answer(f"Произошла ошибка: {str(e)}")