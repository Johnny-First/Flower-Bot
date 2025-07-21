from aiogram import Dispatcher, types, F
from ..config import FLOWERS_PICTURES, FLOWERS_CAPTIONS, get_order_keyboard

class FlowerHandlers:
    def __init__(self, dp: Dispatcher):
        dp.callback_query.register(self.send_flower_image, F.data.in_(FLOWERS_PICTURES.keys()))
            
    async def send_flower_image(self, callback: types.CallbackQuery):
        flower_type = callback.data
        try:
            await callback.message.edit_media(
                types.InputMediaPhoto(
                    media=FLOWERS_PICTURES[flower_type], 
                    caption=FLOWERS_CAPTIONS.get(flower_type, "Красивый цветок!")
                ),
                reply_markup=get_order_keyboard()
            )
            await callback.answer() 
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)