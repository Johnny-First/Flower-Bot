from aiogram import types
from typing import Dict
from ..database.models import CategoryManager, FlowerManager

def get_my_keyboard(role: str, data: Dict[str, str]) -> types.InlineKeyboardMarkup:
    buttons = []
    row = []
    for name, callback in data.items():  
        row.append(types.InlineKeyboardButton(
            text=name, 
            callback_data=f"{role}{callback}"
        ))
        if len(row) == 2:  
            buttons.append(row)
            row = []
    if row:  
        buttons.append(row)
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_base_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Заказать цветы", callback_data="catalog")]
        ]
    )

def get_admin_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Рассылка", callback_data="admin_mailing"),
             types.InlineKeyboardButton(text="Взаимодействие с каталогом", callback_data="admin_interact_catalog")],
            [types.InlineKeyboardButton(text="📋 Проверить готовых к заказу", callback_data="admin_orders")],
            [types.InlineKeyboardButton(text="📊 Все заказы (включая выполненные)", callback_data="admin_all_orders")]
        ]
    )

def get_pay_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Проверить корзину", callback_data="check_cart")],
            [types.InlineKeyboardButton(text="В каталог", callback_data="catalog")]
        ]
    )
async def admin_get_categories_keyboard():
    categories = await CategoryManager.get_all_categories()
    buttons = []
    row = []
    for category_id in categories:
        row.append(types.InlineKeyboardButton(text=category_id[0], callback_data=f"{category_id[1]}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([types.InlineKeyboardButton(text="Назад", callback_data="admin_interact_catalog")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_categories_keyboard():
    categories = await CategoryManager.get_available_categories()
    buttons = []
    row = []
    if not categories:
        buttons.append([types.InlineKeyboardButton(text="Простите, цветы кончились! Загляните завтра)", callback_data="no_categories")])
    else:
        for category_id in categories:
            row.append(types.InlineKeyboardButton(text=category_id[0], callback_data=f"category_{category_id[1]}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
    buttons.append([types.InlineKeyboardButton(text="Посмотреть корзину", callback_data="check_cart")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_flowers_keyboard(category_id):
    flowers = await FlowerManager.get_flowers_by_category(category_id)
    buttons = []
    
    if not flowers:
        buttons.append([types.InlineKeyboardButton(text="В этой категории пока нет цветов", callback_data="no_flowers")])
    else:
        # Разделяем цветы на те, что в наличии и нет
        in_stock_flowers = []
        out_of_stock_flowers = []
        
        for flower in flowers:
            # flower[6] - предположительно 7-й элемент (in_stock), индексация с 0
            if flower[6] == 1:  # в наличии
                in_stock_flowers.append(flower)
            else:  # нет в наличии
                out_of_stock_flowers.append(flower)
        row = []
        for flower in in_stock_flowers:
            row.append(types.InlineKeyboardButton(text=flower[1], callback_data=f"flower_{flower[0]}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        
        # Добавляем разделитель для цветов не в наличии
        if out_of_stock_flowers:
            buttons.append([types.InlineKeyboardButton(text="НЕТ В НАЛИЧИИ:", callback_data="out_of_stock_header")])
            
            # Добавляем цветы не в наличии
            row = []
            for flower in out_of_stock_flowers:
                row.append(types.InlineKeyboardButton(text= flower[1], callback_data=f"flower_{flower[0]}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
    buttons.append([types.InlineKeyboardButton(text="Посмотреть корзину", callback_data="check_cart")])
    buttons.append([types.InlineKeyboardButton(text="Назад", callback_data="catalog")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

async def admin_get_flowers_keyboard(category_id):
    flowers = await FlowerManager.get_flowers_by_category(category_id)
    buttons = []
    
    if not flowers:
        buttons.append([types.InlineKeyboardButton(text="В этой категории пока нет цветов", callback_data="no_flowers")])
    else:
        # Разделяем цветы на те, что в наличии и нет
        in_stock_flowers = []
        out_of_stock_flowers = []
        
        for flower in flowers:
            if flower[6] == 1:  # в наличии
                in_stock_flowers.append(flower)
            else:  # нет в наличии
                out_of_stock_flowers.append(flower)
        
        # Сначала добавляем цветы в наличии
        row = []
        for flower in in_stock_flowers:
            row.append(types.InlineKeyboardButton(text=flower[1], callback_data=f"{flower[0]}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        
        # Добавляем разделитель для цветов не в наличии
        if out_of_stock_flowers:
            buttons.append([types.InlineKeyboardButton(text="НЕТ В НАЛИЧИИ:", callback_data="out_of_stock_header")])
            
            # Добавляем цветы не в наличии
            row = []
            for flower in out_of_stock_flowers:
                row.append(types.InlineKeyboardButton(text=flower[1], callback_data=f"{flower[0]}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
    
    buttons.append([types.InlineKeyboardButton(text="Назад", callback_data="admin_interact_catalog")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_keyboard(category_id, flower_id, stock):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_cart_{flower_id}")],
            [types.InlineKeyboardButton(text="Посмотрим другие", callback_data=f"back_{category_id}")]
        ]
    )
