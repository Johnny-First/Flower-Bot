from aiogram.fsm.state import StatesGroup, State
from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, admin_get_flowers_keyboard, get_my_keyboard, admin_get_categories_keyboard
import sqlite3
from aiogram.filters import StateFilter
import os
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from ..database.models import FlowerManager, CategoryManager
from ..config import get_admin_keyboard

class AdminStates(StatesGroup):
    waiting_broadcast = State() 
    waiting_new_category_name = State()
    waiting_new_flower = State()
    waiting_category_delete = State()
    waiting_flower_delete = State()
    waiting_flower_category = State()
    waiting_to_stop = State()

class AdminHandlers:
    def __init__(self, dp: Dispatcher):
        load_dotenv()
        self.admin_ids = os.getenv("ADMIN_IDS", "")
        self.admin_ids = [int(x) for x in self.admin_ids.split(",") if x.strip()]

        dp.message.register(self.admin_panel, Command("admin"))        

        dp.callback_query.register(
            self.admin_action_callback,
            F.data.startswith("admin") 
        )

        dp.message.register(
            self.broadcast_message,
            StateFilter(AdminStates.waiting_broadcast)
        )
        dp.callback_query.register(
            self.stop_flower,
            StateFilter(AdminStates.waiting_to_stop)
        )
        dp.callback_query.register(
            self.remove_category,
            StateFilter(AdminStates.waiting_category_delete)
        )
        dp.callback_query.register(
            self.delete_flower,
            StateFilter(AdminStates.waiting_flower_delete)
        )
        dp.message.register(
            self.process_new_category,
            StateFilter(AdminStates.waiting_new_category_name)
        )
        dp.message.register(
            self.process_new_flower,
            StateFilter(AdminStates.waiting_new_flower)
        )
        dp.callback_query.register(
            self.flower_category,
            StateFilter(AdminStates.waiting_flower_category)
        )
        
        

    async def admin_panel(self, message: types.Message):        
        if message.from_user.id not in self.admin_ids:
            await message.answer("У вас нет доступа к админ-панели.")
            return
        await message.answer(
            "Что бы вы хотели сделать, админ?",
            reply_markup=get_admin_keyboard()
        )
 

    async def admin_action_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        data = "_".join(callback.data.split("_")[1:])
        if callback.from_user.id not in self.admin_ids:
            await callback.answer("Нет доступа", show_alert=True)
            return
        
        if data == "mailing":
            await callback.message.answer("Введите текст для рассылки:")
            await state.set_state(AdminStates.waiting_broadcast)  
            await callback.answer()
            
        elif data == "interact_catalog":
            await state.clear()
            await callback.message.edit_text("Опции:", reply_markup=get_my_keyboard(
                "admin", 
                {
                    "Добавить/изменить категорию": "category_add",
                    "Удалить категорию": "category_remove",
                    "Добавить товар": "flower_add",
                    "Поставить на стоп/вывести из стопа товар": "flower_stop",
                    "Удалить товар": "flower_remove"
                }
            ))
            await callback.answer()
            
        elif data == "category_add":
            names = await CategoryManager.get_all_categories()
            names = "\n".join([f"Наименование: {name}, статус: {"в наличии" if in_stock == 1 else "нет в наличии"}, id: {id}" for name, id, in_stock in names])
            await callback.message.edit_text(f"Введите имя новой категории, если её пока нет в наличии добавьте 0 через пробел, например: Розы 0, если их нет или Розы, если они есть\n\nДоступные категории:\n\n{names}", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Назад", callback_data="admin_interact_catalog")]]))
            await state.set_state(AdminStates.waiting_new_category_name)
            await callback.answer()
        
        elif data == "category_remove":
            await callback.message.edit_text(text="Выберите категорию, которую хотите убрать.\nВнимание! "
                                             "Это удалит все цветы этой категории. Если хотите поставить категорию "
                                             "на стоп воспользуйтесь пунктом изменить категорию", reply_markup=await admin_get_categories_keyboard())
            await state.set_state(AdminStates.waiting_category_delete)
            
            await callback.answer()
        
        elif data == "flower_add":
            await callback.message.edit_text("Укажите категорию, в которую хотите добавить цветок",  reply_markup=await admin_get_categories_keyboard())
            await state.set_state(AdminStates.waiting_flower_category)
            await state.update_data(action="add")
            await callback.answer()
        elif data == 'flower_remove':
            await callback.message.edit_text(text='Выберите цветок для удаления', reply_markup=await admin_get_categories_keyboard())
            await state.set_state(AdminStates.waiting_flower_category)
            await state.update_data(action="remove")
            await callback.answer()
        elif data == 'flower_stop':
            await callback.message.edit_text("Выберите категорию", reply_markup=await admin_get_categories_keyboard())
            await state.set_state(AdminStates.waiting_flower_category)
            await state.update_data(action="stop")
            await callback.answer()
        elif data == "orders":
            await self.show_orders(callback)
            await callback.answer()
        else:
            await callback.answer("Неизвестное действие", show_alert=True)

    async def flower_category(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()  
        action = data.get("action")    
        category_id = int(callback.data)
        await state.update_data(category_id=category_id)
        if action == "add":
            await callback.message.edit_text("Введите карточку товара по образцу(прикрепите фото): Число_слов_в_наименовании Наименование Цена Подпись")
            await state.set_state(AdminStates.waiting_new_flower)
        if action == "remove":
            await callback.message.edit_text("Выберите цветок для удаления:", reply_markup=await admin_get_flowers_keyboard(category_id=category_id))
            await state.set_state(AdminStates.waiting_flower_delete)
        if action == "stop":
            await callback.message.edit_text(text="Какой товар запускаем/стопим?", reply_markup=await admin_get_flowers_keyboard(category_id=category_id))
            await state.set_state(AdminStates.waiting_to_stop)
        await callback.answer()

    async def stop_flower(self, callback: types.CallbackQuery, state: FSMContext):

        await FlowerManager.stop_flower(int(callback.data))
        await callback.message.edit_text("Успешно! Что-нибудь еще?", reply_markup=get_admin_keyboard())
        await callback.answer()
        await state.set_data({})
        await state.clear()


    async def process_new_category(self, message: types.Message, state: FSMContext):
        input_text = message.text.strip()
        
        if input_text.endswith(' 0'):
            category_name = input_text[:-2].strip()
            stock_value = 0
        elif input_text.endswith(' 1'):
            category_name = input_text[:-2].strip()
            stock_value = 1
        else:
            category_name = input_text
            stock_value = 1
        
        try:
            await CategoryManager.add_category(category_name, stock_value)
            status = "в наличии" if stock_value == 1 else "нет в наличии"
            await message.answer(
                f"Категория '{category_name}' добавлена/изменена! Статус: {status}",
                reply_markup=get_admin_keyboard()
            )
        except Exception as e:
            await message.answer(f"Ошибка при добавлении категории: {e}")
        
        await state.clear()
    

    async def remove_category(self, callback: types.CallbackQuery, state: FSMContext):
        cat_id = int(callback.data)
        try:
            await CategoryManager.delete_category(cat_id)
            await callback.message.edit_text("Категория успешно удалена! Что-то еще?", reply_markup=get_admin_keyboard())    
        except Exception as e:
            await callback.answer(f"Ошибка: {e}", show_alert=True)
        finally:
            await callback.answer()
        await state.clear()
    

    async def delete_flower(self, callback: types.CallbackQuery, state: FSMContext):
        flower_id = callback.data
        await FlowerManager.delete_flower(flower_id=int(flower_id))
        await callback.message.edit_text("Успешно! Что-то еще?", reply_markup=get_admin_keyboard())
        
        await callback.answer()
        await state.clear()

    async def process_new_flower(self, message: types.Message, state: FSMContext):
        if not message.caption:
            await message.answer("Чего-то не хватает! Нужен формат: 'Число Наименование Цена Описание' + Фото!")
            return
        try:
            
            parts = message.caption.split()

            num_words = int(parts[0])

            name = " ".join(parts[1:1+num_words])

            price = float(parts[1+num_words])

            description = " ".join(parts[2+num_words:])

            file_id = None
            if message.photo:
                file_id = message.photo[-1].file_id

            data = await state.get_data()
            category_id = data.get('category_id')

            if not category_id:
                await message.answer("Ошибка: не найдена категория")
                return

            await FlowerManager.add_flower(name, price, description, file_id, category_id)
            await message.answer(
            f"Цветок добавлен!\nНазвание: {name}\nЦена: {price}\nОписание: {description}",
            reply_markup=get_admin_keyboard()
        )
        except (ValueError, IndexError) as e:
            await message.answer(
                "Ошибка формата! Используйте: 'Число Наименование Цена Описание'\n"
                "Пример: '2 Роза красная 500 Красивая красная роза'"
            )
        except Exception as e:
                await message.answer(f"Ошибка при добавлении: {e}")
        await state.set_data({})
        await state.clear()

    async def broadcast_message(self, message: types.Message, state: FSMContext):
        broadcast_text = message.text
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        sent = 0
        for user_id in user_ids:
            try:
                await message.bot.send_message(user_id, broadcast_text)
                sent += 1
            except Exception:
                continue
        
        await message.answer(
            f"Рассылка завершена. Сообщение отправлено {sent} пользователям.",
            reply_markup=get_admin_keyboard()
        )
        await state.clear()

    async def show_orders(self, callback: types.CallbackQuery):
        """Показать все заказы в админ-панели"""
        try:
            from ..database.models import CheckoutManager
            import json
            
            # Получаем все заказы
            orders = await CheckoutManager.get_all_orders()
            
            if not orders:
                await callback.message.edit_text(
                    "📋 Заказов пока нет",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Назад", callback_data="admin")]
                        ]
                    )
                )
                return
            
            # Формируем таблицу заказов
            orders_text = "📋 Список заказов:\n\n"
            
            for i, order in enumerate(orders, 1):
                order_id, user_id, username, first_name, last_name, phone, customer_name, cart_items, total_price, order_date, status = order
                
                # Парсим товары из JSON
                try:
                    items = json.loads(cart_items)
                    items_text = ""
                    for item in items:
                        items_text += f"  • {item['name']} × {item['quantity']} = {item['quantity'] * item['price']}₽\n"
                except:
                    items_text = "  • Ошибка чтения товаров\n"
                
                orders_text += f"🔸 Заказ #{order_id}\n"
                orders_text += f"👤 Клиент: {customer_name}\n"
                orders_text += f"📱 Телефон: {phone}\n"
                orders_text += f"💰 Сумма: {total_price}₽\n"
                orders_text += f"📅 Дата: {order_date}\n"
                orders_text += f"📦 Статус: {status}\n"
                orders_text += f"🛒 Товары:\n{items_text}\n"
                orders_text += "─" * 40 + "\n\n"
                
                # Ограничиваем длину сообщения
                if len(orders_text) > 3000:
                    orders_text = orders_text[:3000] + "...\n\n(Показаны первые заказы)"
                    break
            
            # Добавляем кнопки управления
            keyboard = []
            for order in orders[:5]:  # Показываем кнопки только для первых 5 заказов
                order_id = order[0]
                keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"✅ Выполнен #{order_id}", 
                        callback_data=f"complete_order_{order_id}"
                    )
                ])
            
            keyboard.append([types.InlineKeyboardButton(text="Назад", callback_data="admin")])
            
            await callback.message.edit_text(
                orders_text,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при загрузке заказов: {str(e)}",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Назад", callback_data="admin")]
                    ]
                )
            )
        
        