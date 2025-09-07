from aiogram.fsm.state import StatesGroup, State
from aiogram import F, types, Dispatcher
from aiogram.filters import Command  
from ..config import get_base_keyboard, admin_get_flowers_keyboard, get_my_keyboard, admin_get_categories_keyboard
import sqlite3
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from ..database.models import FlowerManager, CategoryManager
from ..config import get_admin_keyboard
from ..config.settings import settings

class AdminStates(StatesGroup):
    waiting_broadcast = State() 
    waiting_new_category_name = State()
    waiting_new_category_photo = State()
    waiting_flower_name = State()
    waiting_flower_price = State()
    waiting_flower_caption = State()
    waiting_flower_photo = State()
    waiting_flower_category = State()
    waiting_category_delete = State()
    waiting_flower_delete = State()
    waiting_to_stop = State()

class AdminHandlers:
    def __init__(self, dp: Dispatcher):
        self.admin_ids = [int(x) for x in settings.ADMIN_IDS.split(",") if x.strip()]

        dp.message.register(self.admin_panel, Command("admin"))
        dp.callback_query.register(self.admin_panel_callback, F.data == "admin")        

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
            self.process_new_category_photo,
            StateFilter(AdminStates.waiting_new_category_photo)
        )
        dp.message.register(
            self.process_flower_name,
            StateFilter(AdminStates.waiting_flower_name)
        )
        dp.message.register(
            self.process_flower_price,
            StateFilter(AdminStates.waiting_flower_price)
        )
        dp.message.register(
            self.process_flower_caption,
            StateFilter(AdminStates.waiting_flower_caption)
        )
        dp.message.register(
            self.process_flower_photo,
            StateFilter(AdminStates.waiting_flower_photo)
        )
        dp.message.register(
            self.broadcast_message,
            StateFilter(AdminStates.waiting_broadcast)
        )
        dp.callback_query.register(
            self.flower_category,
            StateFilter(AdminStates.waiting_flower_category)
        )
        dp.callback_query.register(
            self.complete_order,
            F.data.startswith("complete_order_")
        )
        

    async def admin_panel(self, message: types.Message, state: FSMContext):
        await state.clear()        
        if message.from_user.id not in self.admin_ids:
            await message.answer("У вас нет доступа к админ-панели.")
            return
        await message.answer(
            "Что бы вы хотели сделать, админ?",
            reply_markup=get_admin_keyboard()
        )

    async def admin_panel_callback(self, callback: types.CallbackQuery, state: FSMContext):     
        await state.clear()           
        if callback.from_user.id not in self.admin_ids:
            await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
            return
        await callback.message.edit_text(
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
            await callback.message.answer("📢 Отправьте текст для рассылки.\n\n💡 Вы также можете отправить фотографию с подписью - она будет разослана всем пользователям.", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Назад", callback_data="admin_interact_catalog")]]))
            await state.set_state(AdminStates.waiting_broadcast)
            await callback.answer()
            
        elif data == "interact_catalog":
            await state.clear()
            await callback.message.edit_text("Опции:", reply_markup=get_my_keyboard(
                "admin", 
                {
                    "Добавить/изменить категорию": "_category_add",
                    "Удалить категорию": "_category_remove",
                    "Добавить товар": "_flower_add",
                    "Поставить на стоп/вывести из стопа товар": "_flower_stop",
                    "Удалить товар": "_flower_remove",
                    "Назад": ""
                }
            ))
            await callback.answer()
            
        elif data == "category_add":
            await callback.message.edit_text(
                "📝 Введите название новой категории:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                        types.InlineKeyboardButton(text="Назад", callback_data="admin_interact_catalog")
                    ]]
                )
            )
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
        elif data == "all_orders":
            await self.show_all_orders(callback)
            await callback.answer()
        elif callback.data == "admin_flower_add":
            await callback.message.edit_text(
                "🌹 Добавление нового цветка\n\n📝 Введите название цветка:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
            await state.set_state(AdminStates.waiting_flower_name)
            await callback.answer()
        else:
            await callback.answer("Неизвестное действие", show_alert=True)

    async def flower_category(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()  
        action = data.get("action")    
        category_id = int(callback.data)
        await state.update_data(category_id=category_id)
        
        if action == "add":
            # Сохраняем выбранную категорию и запрашиваем название цветка
            await state.update_data(flower_category_id=category_id)
            await state.set_state(AdminStates.waiting_flower_name)
            await callback.message.edit_text(
                "🌹 Добавление нового цветка\n\n📝 Введите название цветка:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
        elif action == "remove":
            await callback.message.edit_text("Выберите цветок для удаления:", reply_markup=await admin_get_flowers_keyboard(category_id=category_id))
            await state.set_state(AdminStates.waiting_flower_delete)
        elif action == "stop":
            await callback.message.edit_text(text="Какой товар запускаем/стопим?", reply_markup=await admin_get_flowers_keyboard(category_id=category_id))
            await state.set_state(AdminStates.waiting_to_stop)
        
        await callback.answer()

    async def complete_order(self, callback: types.CallbackQuery):
        """Отметить заказ как выполненный"""
        try:
            from ..database.models import CheckoutManager
            
            # Извлекаем ID заказа из callback_data: "complete_order_123" -> 123
            order_id = int(callback.data.split("_")[-1])
            
            # Обновляем статус заказа на "completed"
            await CheckoutManager.update_order_status(order_id, "completed")
            
            await callback.answer("✅ Заказ отмечен как выполненный!", show_alert=True)
            
            # Обновляем список заказов (убираем выполненный)
            await self.show_orders(callback)
            
        except Exception as e:
            await callback.answer(f"Ошибка при обновлении заказа: {str(e)}", show_alert=True)

    async def stop_flower(self, callback: types.CallbackQuery, state: FSMContext):
        try:
            # Проверяем, что callback.data содержит числовой ID цветка
            if not callback.data.isdigit():
                await callback.answer("Неверный ID цветка", show_alert=True)
                return
                
            flower_id = int(callback.data)
            await FlowerManager.stop_flower(flower_id)
            await callback.message.edit_text("Успешно! Что-нибудь еще?", reply_markup=get_admin_keyboard())
            await callback.answer()
            await state.set_data({})
            await state.clear()
            
        except ValueError:
            await callback.answer("Неверный ID цветка", show_alert=True)
        except Exception as e:
            await callback.answer(f"Ошибка при обновлении статуса: {str(e)}", show_alert=True)


    async def process_new_category(self, message: types.Message, state: FSMContext):
        input_text = message.text.strip()
        
        # Простая валидация названия
        if len(input_text) < 2:
            await message.answer("Название категории слишком короткое. Попробуйте еще раз.")
            return
        
        try:
            # Сохраняем название категории в state
            await state.update_data(category_name=input_text)
            
            # Запрашиваем фотографию категории
            await state.set_state(AdminStates.waiting_new_category_photo)
            await message.answer(
                "📸 Теперь отправьте фотографию для категории:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
            
        except Exception as e:
            await message.answer(f"Ошибка при обработке названия: {e}")
            await state.clear()
    

    async def process_new_category_photo(self, message: types.Message, state: FSMContext):
        if not message.photo:
            await message.answer("Пожалуйста, отправьте фотографию категории.")
            return

        try:
            photo_file_id = message.photo[-1].file_id
            await state.update_data(category_photo_file_id=photo_file_id)

            # Получаем данные из state с await
            data = await state.get_data()
            category_name = data["category_name"]
            category_photo_file_id = data["category_photo_file_id"]

            await CategoryManager.add_category(category_name, category_photo_file_id)
            await message.answer(
                f"Категория '{category_name}' успешно добавлена!",
                reply_markup=get_admin_keyboard()
            )
            await state.clear()

        except Exception as e:
            await message.answer(f"Ошибка при добавлении категории: {e}")
            await state.clear()

    async def process_flower_name(self, message: types.Message, state: FSMContext):
        """Обработчик ввода названия цветка"""
        flower_name = message.text.strip()
        
        if len(flower_name) < 2:
            await message.answer("Название цветка слишком короткое. Попробуйте еще раз.")
            return
        
        try:
            # Сохраняем название цветка в state
            await state.update_data(flower_name=flower_name)
            
            # Запрашиваем цену
            await state.set_state(AdminStates.waiting_flower_price)
            await message.answer(
                "💰 Теперь введите цену цветка (только число):",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
            
        except Exception as e:
            await message.answer(f"Ошибка при обработке названия: {e}")
            await state.clear()

    async def process_flower_price(self, message: types.Message, state: FSMContext):
        """Обработчик ввода цены цветка"""
        try:
            price = float(message.text.strip())
            if price <= 0:
                await message.answer("Цена должна быть положительным числом. Попробуйте еще раз.")
                return
            
            # Сохраняем цену в state
            await state.update_data(flower_price=price)
            
            # Запрашиваем описание
            await state.set_state(AdminStates.waiting_flower_caption)
            await message.answer(
                "📝 Теперь введите описание цветка:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
            
        except ValueError:
            await message.answer("Пожалуйста, введите только число для цены.")
        except Exception as e:
            await message.answer(f"Ошибка при обработке цены: {e}")
            await state.clear()

    async def process_flower_caption(self, message: types.Message, state: FSMContext):
        """Обработчик ввода описания цветка"""
        caption = message.text.strip()
        

        try:
            # Сохраняем описание в state
            await state.update_data(flower_caption=caption)
            
            # Запрашиваем фотографию цветка
            await state.set_state(AdminStates.waiting_flower_photo)
            await message.answer(
                "📸 Теперь отправьте фотографию цветка:",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Отмена", callback_data="admin_interact_catalog")]
                    ]
                )
            )
            
        except Exception as e:
            await message.answer(f"Ошибка при обработке описания: {e}")
            await state.clear()

    async def process_flower_photo(self, message: types.Message, state: FSMContext):
        """Обработчик фотографии цветка"""
        if not message.photo:
            await message.answer("Пожалуйста, отправьте фотографию цветка.")
            return

        try:
            photo_file_id = message.photo[-1].file_id
            
            data = await state.get_data()
            flower_name = data["flower_name"]
            flower_price = data["flower_price"]
            flower_caption = data["flower_caption"]
            flower_category_id = data["flower_category_id"]
            
            await FlowerManager.add_flower(
                name=flower_name,
                price=str(flower_price),
                caption=flower_caption,
                photo_id=photo_file_id,
                category_id=flower_category_id
            )
            
            await message.answer(
                f"✅ Цветок '{flower_name}' успешно добавлен!\n\n"
                f"🌹 Название: {flower_name}\n"
                f"💰 Цена: {flower_price}₽\n"
                f"📝 Описание: {flower_caption}\n"
                f"📂 Категория ID: {flower_category_id}",
                reply_markup=get_admin_keyboard()
            )
            await state.clear()
            
        except Exception as e:
            await message.answer(f"Ошибка при добавлении цветка: {e}")
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

    async def broadcast_message(self, message: types.Message, state: FSMContext):
        """Обработчик рассылки сообщений и фотографий"""
        from ..database.models import UserManager
        
        try:
            # Получаем всех пользователей
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            user_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            sent = 0
            failed = 0
            
            if message.photo:
                # Рассылка фотографии с подписью
                photo_file_id = message.photo[-1].file_id
                caption = message.caption or ""
                
                for user_id in user_ids:
                    try:
                        await message.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_file_id,
                            caption=caption
                        )
                        sent += 1
                    except Exception as e:
                        print(f"Ошибка отправки фото пользователю {user_id}: {e}")
                        failed += 1
                        continue
                        
                result_message = f"📸 Рассылка фотографии завершена!\n✅ Отправлено: {sent} пользователям"
                if failed > 0:
                    result_message += f"\n❌ Ошибки: {failed} пользователей"
                    
            else:
                # Рассылка только текста
                broadcast_text = message.text
                
                for user_id in user_ids:
                    try:
                        await message.bot.send_message(
                            chat_id=user_id,
                            text=broadcast_text
                        )
                        sent += 1
                    except Exception as e:
                        print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                        failed += 1
                        continue
                        
                result_message = f"📢 Рассылка текста завершена!\n✅ Отправлено: {sent} пользователям"
                if failed > 0:
                    result_message += f"\n❌ Ошибки: {failed} пользователей"
            
            await message.answer(
                result_message,
                reply_markup=get_admin_keyboard()
            )
            
        except Exception as e:
            await message.answer(
                f"❌ Ошибка при рассылке: {str(e)}",
                reply_markup=get_admin_keyboard()
            )
        finally:
            await state.clear()

    async def show_orders(self, callback: types.CallbackQuery):
        """Показать все незавершенные заказы в админ-панели"""
        try:
            from ..database.models import CheckoutManager
            import json
            all_orders = await CheckoutManager.get_all_orders()
            orders = [order for order in all_orders if order[10] != 'completed']  # order[10] - это status
            
            if not orders:
                await callback.message.edit_text(
                    "📋 Активных заказов нет",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Назад", callback_data="admin")]
                        ]
                    )
                )
                return
            
            # Формируем таблицу заказов
            orders_text = "📋 Список активных заказов:\n\n"
            
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

    async def show_all_orders(self, callback: types.CallbackQuery):
        """Показать все заказы (включая выполненные) в админ-панели"""
        try:
            from ..database.models import CheckoutManager
            import json
            
            # Получаем все заказы
            orders = await CheckoutManager.get_all_orders()
            
            if not orders:
                await callback.message.edit_text(
                    "📊 Заказов пока нет",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [types.InlineKeyboardButton(text="Назад", callback_data="admin")]
                        ]
                    )
                )
                return
            
            # Формируем таблицу заказов
            orders_text = "📊 Все заказы (включая выполненные):\n\n"
            
            completed_count = 0
            pending_count = 0
            
            for i, order in enumerate(orders, 1):
                order_id, user_id, username, first_name, last_name, phone, customer_name, cart_items, total_price, order_date, status = order
                
                # Подсчитываем статистику
                if status == 'completed':
                    completed_count += 1
                else:
                    pending_count += 1
                
                # Парсим товары из JSON
                try:
                    items = json.loads(cart_items)
                    items_text = ""
                    for item in items:
                        items_text += f"  • {item['name']} × {item['quantity']} = {item['quantity'] * item['price']}₽\n"
                except:
                    items_text = "  • Ошибка чтения товаров\n"
                
                # Добавляем эмодзи в зависимости от статуса
                status_emoji = "✅" if status == 'completed' else "⏳"
                
                orders_text += f"{status_emoji} Заказ #{order_id}\n"
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
            
            # Добавляем статистику в начало
            stats_text = f"📊 Статистика:\n⏳ Активных: {pending_count} | ✅ Выполненных: {completed_count}\n\n"
            orders_text = stats_text + orders_text
            
            # Добавляем кнопки управления только для активных заказов
            keyboard = []
            active_orders = [order for order in orders if order[10] != 'completed']
            for order in active_orders[:5]:  # Показываем кнопки только для первых 5 активных заказов
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
                f"Ошибка при загрузке всех заказов: {str(e)}",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Назад", callback_data="admin")]
                    ]
                )
            )
        
        