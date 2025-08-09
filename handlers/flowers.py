from aiogram import Dispatcher, types, F
from ..config import FLOWERS_PICTURES, FLOWERS_CAPTIONS, get_order_keyboard, get_flowers_keyboard, get_categories_keyboard
from ..database import get_media_flower, get_flower_category

class FlowerHandlers:
    def __init__(self, dp: Dispatcher):
        dp.callback_query.register(self.send_flower, F.data.startswith("flower_"))
        dp.callback_query.register(self.send_categories, F.data.startswith("category_"))

    async def send_categories(self, callback: types.CallbackQuery):
        flowers_keyboard = await get_flowers_keyboard(category_id=callback.data.split("_")[1])
       
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=FLOWERS_PICTURES["default"], 
                caption="Выберите цветок из категории:"),
            reply_markup=flowers_keyboard
        )
        await callback.answer()

    async def send_flower(self, callback: types.CallbackQuery):
        flower_id = callback.data.split("_")[1]
        media = await get_media_flower(flower_id=flower_id)
        try:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                media=media[2], 
                caption=media[1]),
                reply_markup=get_order_keyboard(await get_flower_category(flower_id=flower_id))
            )
            await callback.answer() 
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)