from aiogram import Dispatcher, types, F
from ..services import CartManager
from ..config import get_pay_keyboard
from ..database.models import FlowerManager
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from aiogram.filters import StateFilter 
import json

class QuantityStates(StatesGroup):
    waiting_state = State()

class CheckoutStates(StatesGroup):
    waiting_phone = State()
    waiting_name = State()

class PaymentHandlers:
    def __init__(self, dp: Dispatcher):
        dp.callback_query.register(self.payment_handler, F.data.startswith("add_cart"))
        dp.callback_query.register(self.list_cart, F.data == "check_cart")
        dp.callback_query.register(self.clear_cart, F.data == "clear_cart")
        dp.callback_query.register(self.checkout_handler, F.data == "checkout")
        dp.callback_query.register(self.cancel_checkout, F.data == "cancel_checkout")
        dp.message.register(
            self.quantity_input_handler,
            StateFilter(QuantityStates.waiting_state)
        )
        dp.message.register(
            self.phone_input_handler,
            StateFilter(CheckoutStates.waiting_phone)
        )
        dp.message.register(
            self.name_input_handler,
            StateFilter(CheckoutStates.waiting_name)
        )
    async def list_cart(self, callback: types.CallbackQuery):
        
        try:
            from ..database.models import UserManager
            
            cart = await UserManager.get_cart(user_id=callback.from_user.id)
            items = cart['items']
            total_price = cart['total_price']
            
            if not items:
                caption = "Ваша корзина пуста"
            else:
                caption = "Ваша корзина:\n\n"
                for item in items:
                    name = item['name']
                    quantity = item['quantity']
                    price = item['price']
                    item_total = quantity * price
                    caption += f"🌹 {name}: {quantity} шт. × {price}₽ = {item_total}₽\n"
                
                caption += f"\n💰 Общая стоимость: {total_price}₽"
            
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                    media=callback.message.photo[-1].file_id if callback.message.photo else "AgACAgIAAxkBAAMQaHGe30jHWjEc3XIWhpNWHIgLWroAAsn-MRsbo5BLMRbcsf9Zu8MBAAMCAAN4AAM2BA",
                    caption=caption
                ),
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")],
                        [types.InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")],
                        [types.InlineKeyboardButton(text="В каталог", callback_data="catalog")]
                    ]
                )
            )
            await callback.answer()
            
        except Exception as e:
            await callback.answer(f"Ошибка при загрузке корзины: {str(e)}", show_alert=True)

    async def clear_cart(self, callback: types.CallbackQuery):
        """Очистка корзины пользователя"""
        try:
            from ..database.models import UserManager
            
            # Очищаем корзину
            success = await UserManager.clear_cart(user_id=callback.from_user.id)
            
            if success:
                await callback.message.edit_media(
                    media=types.InputMediaPhoto(
                        media=callback.message.photo[-1].file_id if callback.message.photo else "AgACAgIAAxkBAAMQaHGe30jHWjEc3XIWhpNWHIgLWroAAsn-MRsbo5BLMRbcsf9Zu8MBAAMCAAN4AAM2BA",
                        caption="✅ Корзина успешно очищена!"
                    ),
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="В каталог", callback_data="catalog")]
                        ]
                    )
                )
                await callback.answer("Корзина очищена!")
            else:
                await callback.answer("Ошибка при очистке корзины", show_alert=True)
                
        except Exception as e:
            await callback.answer(f"Ошибка при очистке корзины: {str(e)}", show_alert=True)

    async def checkout_handler(self, callback: types.CallbackQuery, state: FSMContext):
        """Начало оформления заказа"""
        try:
            from ..database.models import UserManager
            
            # Проверяем, есть ли товары в корзине
            cart = await UserManager.get_cart(user_id=callback.from_user.id)
            if not cart['items']:
                await callback.answer("Ваша корзина пуста!", show_alert=True)
                return
            
            # Сохраняем данные корзины в state
            await state.update_data(
                cart_items=cart['items'],
                total_price=cart['total_price']
            )
            
            # Запрашиваем номер телефона
            await state.set_state(CheckoutStates.waiting_phone)
            await callback.message.edit_media(
                media=types.InputMediaPhoto(
                    media=callback.message.photo[-1].file_id if callback.message.photo else "AgACAgIAAxkBAAMQaHGe30jHWjEc3XIWhpNWHIgLWroAAsn-MRsbo5BLMRbcsf9Zu8MBAAMCAAN4AAM2BA",
                    caption="📱 Введите ваш номер телефона для связи:"
                ),
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_checkout")]
                    ]
                )
            )
            await callback.answer()
            
        except Exception as e:
            await callback.answer(f"Ошибка при оформлении заказа: {str(e)}", show_alert=True)

    async def phone_input_handler(self, message: types.Message, state: FSMContext):
        """Обработчик ввода номера телефона"""
        phone = message.text.strip()
        
        # Простая валидация телефона
        if len(phone) < 10:
            await message.answer("Номер телефона слишком короткий. Попробуйте еще раз.")
            return
        
        # Сохраняем телефон и запрашиваем имя
        await state.update_data(phone=phone)
        await state.set_state(CheckoutStates.waiting_name)
        
        await message.answer(
            "👤 Теперь введите ваше имя для заказа:",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_checkout")]
                ]
            )
        )

    async def name_input_handler(self, message: types.Message, state: FSMContext):
        """Обработчик ввода имени"""
        customer_name = message.text.strip()
        
        if len(customer_name) < 2:
            await message.answer("Имя слишком короткое. Попробуйте еще раз.")
            return
        
        try:
            # Получаем все данные из state
            data = await state.get_data()
            cart_items = data['cart_items']
            total_price = data['total_price']
            phone = data['phone']
            
            # Создаем заказ в БД
            from ..database.models import CheckoutManager
            await CheckoutManager.create_order(
                user_id=message.from_user.id,
                username=message.from_user.username or "",
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name or "",
                phone=phone,
                customer_name=customer_name,
                cart_items=json.dumps(cart_items),
                total_price=total_price
            )
            
            # Очищаем корзину
            from ..database.models import UserManager
            await UserManager.clear_cart(user_id=message.from_user.id)
            
            # Отправляем уведомление админам
            await self.notify_admins_about_order(message, cart_items, total_price, customer_name, phone)
            
            # Подтверждаем заказ пользователю
            await message.answer(
                f"✅ Заказ успешно оформлен!\n\n"
                f"👤 Имя: {customer_name}\n"
                f"📱 Телефон: {phone}\n"
                f"💰 Сумма: {total_price}₽\n\n"
                f"Мы свяжемся с вами в ближайшее время!",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="В каталог", callback_data="catalog")]
                    ]
                )
            )
            
            await state.clear()
            
        except Exception as e:
            await message.answer(f"Ошибка при оформлении заказа: {str(e)}")
            await state.clear()

    async def notify_admins_about_order(self, message: types.Message, cart_items: list, total_price: float, customer_name: str, phone: str):
        """Уведомление админов о новом заказе"""
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            admin_ids = os.getenv("ADMIN_IDS", "")
            admin_ids = [int(x) for x in admin_ids.split(",") if x.strip()]
            
            # Формируем сообщение о заказе
            order_text = f"🆕 НОВЫЙ ЗАКАЗ!\n\n"
            order_text += f"👤 Клиент: {customer_name}\n"
            order_text += f"📱 Телефон: {phone}\n"
            order_text += f"💰 Сумма: {total_price}₽\n\n"
            order_text += "🛒 Товары:\n"
            
            for item in cart_items:
                order_text += f"• {item['name']} × {item['quantity']} = {item['quantity'] * item['price']}₽\n"
            

            
            # Отправляем уведомление всем админам
            for admin_id in admin_ids:
                try:
                    await message.bot.send_message(
                        admin_id,
                        order_text,
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [types.InlineKeyboardButton(text="📋 Посмотреть заказы", callback_data="admin_orders")]
                            ]
                        )
                    )
                except Exception as e:
                    print(f"Не удалось отправить уведомление админу {admin_id}: {e}")
                    
        except Exception as e:
            print(f"Ошибка при отправке уведомления админам: {e}")

    async def cancel_checkout(self, callback: types.CallbackQuery, state: FSMContext):
        """Отмена оформления заказа"""
        await state.clear()
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=callback.message.photo[-1].file_id if callback.message.photo else "AgACAgIAAxkBAAMQaHGe30jHWjEc3XIWhpNWHIgLWroAAsn-MRsbo5BLMRbcsf9Zu8MBAAMCAAN4AAM2BA",
                caption="❌ Оформление заказа отменено"
            ),
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="В каталог", callback_data="catalog")]
                ]
            )
        )
        await callback.answer("Оформление заказа отменено")

    async def payment_handler(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработчик добавления в корзину"""
        flower_id = int(callback.data.split("_")[-1])
        await state.update_data(flower_id=flower_id)
        await state.set_state(QuantityStates.waiting_state)
        
        category_id = await FlowerManager.get_flower_category(flower_id)
        await callback.message.edit_media(
            media=types.InputMediaPhoto(
                media=callback.message.photo[-1].file_id if callback.message.photo else "AgACAgIAAxkBAAMQaHGe30jHWjEc3XIWhpNWHIgLWroAAsn-MRsbo5BLMRbcsf9Zu8MBAAMCAAN4AAM2BA",
                caption="Сколько бы вы хотели заказать цветов? (Только число)"
            ),
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(
                        text="Назад", 
                        callback_data=f"back_{category_id}"
                    )
                ]]
            )
        )
        await callback.answer()

    async def quantity_input_handler(self, message: types.Message, state: FSMContext):
        """Обработчик ввода количества"""
        try:
            quantity = int(message.text)
            if quantity <= 0:
                await message.answer("Количество должно быть положительным числом!")
                return
            
            data = await state.get_data()
            flower_id = data.get('flower_id')
            
            if not flower_id:
                await message.answer("Ошибка: не найден ID цветка")
                return
            
            from ..database.models import UserManager
            await UserManager.to_cart(
                user_id=message.from_user.id,
                new_item={"id": flower_id, "quantity": quantity}
            )
            
            await message.answer(
                f"Добавлено {quantity} цветов в корзину!",
                reply_markup=get_pay_keyboard()
            )
            await state.clear()
            
        except ValueError:
            await message.answer("Пожалуйста, введите только число!")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
            await state.clear() 