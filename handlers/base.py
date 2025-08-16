from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, get_categories_keyboard, get_flowers_keyboard
from ..config.media import FLOWERS_PICTURES
import aiosqlite



class BaseHandlers:
    def __init__(self, dp: Dispatcher):
        dp.message.register(self.start_cmd, Command("start"))
        dp.callback_query.register(self.catalog, F.data == "catalog")
        dp.callback_query.register(self.watch_others, F.data.startswith("back_"))


    async def start_cmd(self, message: types.Message):
        from ..database import add_user
        await add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await message.answer(
            "🌸 Добро пожаловать в наш магазинчик цветов!",
            reply_markup=get_base_keyboard()
        )
    
    async def watch_others(self, callback: types.CallbackQuery):
        try:
            await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=FLOWERS_PICTURES["default"], 
                caption="Выберите цветок:"),
            reply_markup=await get_flowers_keyboard(category_id=callback.data.split("_")[1])
        )
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
        finally:
            await callback.answer()

    async def catalog(self, callback: types.CallbackQuery):
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
                reply_markup=await get_categories_keyboard()
            )
            await callback.answer()
        except Exception as e:
            await callback.message.answer(f"Ошибка: {str(e)}")