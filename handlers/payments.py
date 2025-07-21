from aiogram import Dispatcher, types, F
from ..services import PaymentService
from ..config import get_pay_keyboard

class PaymentHandlers:
    def __init__(self, dp: Dispatcher):
        dp.callback_query.register(self.payment_handler, F.data == "order")
        dp.callback_query.register(self.payment_success_handler, F.data == "paid")

    async def payment_handler(self, callback: types.CallbackQuery):
        paylink = PaymentService().create_paylink()
        await callback.message.answer(f"Перейдите по ссылке для оплаты: {paylink}\n\nПосле оплаты нажмите кнопку ниже.",
                                     reply_markup=get_pay_keyboard())
        await callback.answer()

    async def payment_success_handler(self, callback: types.CallbackQuery):
        await callback.message.answer("Оплачено, отлично!")
        await callback.answer()