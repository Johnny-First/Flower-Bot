from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, get_flowers_keyboard
from ..config.media import FLOWERS_PICTURES



class BaseHandlers:
    def __init__(self, dp: Dispatcher):
        dp.message.register(self.start_cmd, Command("start"))
        # dp.message.register(self.about_cmd, F.text == "О магазине")
        dp.message.register(self.order, F.text == "Заказать цветы")
        dp.callback_query.register(self.watch_others, F.data == "back")

    # async def about_cmd(self, message: types.Message):
    #     await message.answer("Мы - цветочный магазин с 2010 года!")
    
    async def start_cmd(self, message: types.Message):
        await message.answer(
            "🌸 Добро пожаловать в наш магазинчик цветов!",
            reply_markup=get_base_keyboard()
        )
    
    async def watch_others(self, callback: types.CallbackQuery):
        try:
            media = types.InputMediaPhoto(
                media=FLOWERS_PICTURES["default"], 
                caption=(
                    "Выберите, какие цветы вам по душе?\n"
                    "Или опишите их, если не знаете названия, а наш ИИ-ассистент "
                    "подскажет вам"
                )
            )
            await callback.message.edit_media(
                media=media,
                reply_markup=get_flowers_keyboard()
            )
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
        finally:
            await callback.answer()

    async def order(self, message: types.Message):
        try:
            await message.answer_photo(
                photo=FLOWERS_PICTURES["default"], 
                caption=(
                    "Выберите, какие цветы вам по душе?\n"
                    "Или опишите их, если не знаете названия, а наш ИИ-ассистент "
                    "подскажет вам"
                ),
                reply_markup=get_flowers_keyboard()
            )
        except Exception as e:
            await message.answer(f"Ошибка: {str(e)}")