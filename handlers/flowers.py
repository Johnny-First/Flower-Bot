from aiogram import Dispatcher, types, F
from ..config import FLOWERS_PICTURES, FLOWERS_CAPTIONS, get_order_keyboard, get_flowers_keyboard, get_categories_keyboard
from ..database.models import FlowerManager

class FlowerHandlers:
    def __init__(self, dp: Dispatcher):
        dp.callback_query.register(self.send_flower, F.data.startswith("flower_"))
        dp.callback_query.register(self.send_categories, F.data.startswith("category_"))

    async def send_categories(self, callback: types.CallbackQuery):
        category_id = callback.data.split("_")[1]
        
        # Получаем фотографию категории
        from ..database.models import CategoryManager
        category_photo_id = await CategoryManager.get_category_photo(int(category_id))
        
        flowers_keyboard = await get_flowers_keyboard(category_id=category_id, category_photo_id=category_photo_id)
        
        # Используем фотографию категории, если она есть, иначе дефолтную
        photo_to_use = category_photo_id if category_photo_id else FLOWERS_PICTURES["default"]
       
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=photo_to_use, 
                caption="Выберите цветок из категории:"
            ),
            reply_markup=flowers_keyboard
        )
        await callback.answer()

    async def send_flower(self, callback: types.CallbackQuery):
        flower_id = callback.data.split("_")[1]
        media = await FlowerManager.get_media_flower(flower_id=flower_id)
        try:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                media=media[2], 
                caption=media[1]),
                reply_markup=get_order_keyboard(await FlowerManager.get_flower_category(flower_id=flower_id), flower_id=flower_id, stock=await FlowerManager.get_flower_stock(flower_id=flower_id))
            )
            await callback.answer() 
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)