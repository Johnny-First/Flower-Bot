from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from aiogram.fsm.context import FSMContext
from ..config import get_base_keyboard, get_categories_keyboard, get_flowers_keyboard
from ..config.media import FLOWERS_PICTURES
import aiosqlite

class BaseHandlers:
    def __init__(self, dp: Dispatcher):
        dp.message.register(self.start_cmd, Command("start"))
        dp.callback_query.register(self.catalog, F.data == "catalog")
        dp.callback_query.register(self.out_stock, F.data == "out_of_stock_header")
        dp.callback_query.register(self.out_stock, F.data == "no_flowers")
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
    async def out_stock(self, callback: types.CallbackQuery):
        if callback.data == "out_of_stock_header": 
            await callback.answer("Ниже представленны цветы, которые вы можете купить в другое время, но сейчас их нет в наличии.")
        await callback.answer()

    async def watch_others(self, callback: types.CallbackQuery, state: FSMContext):
        # Сначала отвечаем на callback, чтобы кнопка не горела
        await callback.answer()
        
        category_id = callback.data.split("_")[1]
        flowers_keyboard = await get_flowers_keyboard(category_id=category_id)
        
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=FLOWERS_PICTURES["default"], 
                caption="Выберите цветок:"
            ),
            reply_markup=flowers_keyboard
        )

    async def catalog(self, callback: types.CallbackQuery, state: FSMContext):
        # Сначала отвечаем на callback, чтобы кнопка не горела
        await callback.answer()
        categories_keyboard = await get_categories_keyboard()
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=FLOWERS_PICTURES["default"],
                caption=(
                    "Выберите, какие цветы вам по душе?\n"
                    "Или опишите их, если не знаете названия, а наш ИИ-ассистент "
                    "подскажет вам"
                )
            ),
            reply_markup=categories_keyboard
        )