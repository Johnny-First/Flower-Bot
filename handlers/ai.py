from aiogram import Dispatcher, types
from ..services.ai import AI_GPT
from ..config import get_base_keyboard

class AI_Handlers:
    def __init__(self, dp: Dispatcher):
        self.gpt = AI_GPT()  
        dp.message.register(
            self.fallback_handler,
            flags={"run_last": True}  
        )
    
    async def fallback_handler(self, message: types.Message):
    
        thinking_msg = await message.answer("ChatGPT печатает...")

        try:
            response = self.gpt.ask_gpt(message.text)
            
            await thinking_msg.delete()
            await message.answer(response, reply_markup=get_base_keyboard())
            
        except Exception as e:
            await thinking_msg.delete()
            await message.answer(f"Произошла ошибка: {str(e)}")