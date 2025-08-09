import aiosqlite
from aiogram import types

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
             types.InlineKeyboardButton(text="Расширение каталога", callback_data="admin_extend_catalog")]
        ]
    )

def get_pay_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Я оплатил", callback_data="paid")],
            [types.InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )

async def get_categories_keyboard():
    async with aiosqlite.connect('users.db') as conn:
        async with conn.execute('SELECT name, id FROM categories WHERE in_stock = 1') as cursor:
            categories = await cursor.fetchall()
    buttons = []
    row = []
    if not categories:
        buttons.append([types.InlineKeyboardButton(text="Нет категорий", callback_data="no_categories")])
    else:
        for category_id in categories:
            row.append(types.InlineKeyboardButton(text=category_id[0], callback_data=f"category_{category_id[1]}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_flowers_keyboard(category_id):
    async with aiosqlite.connect('users.db') as conn:
        async with conn.execute('SELECT * FROM flowers WHERE category_id = ?', (category_id,)) as cursor:
            flowers = await cursor.fetchall()
    buttons = []
    row = []
    if not flowers:
        buttons.append([types.InlineKeyboardButton(text="В этой категории пока нет цветов", callback_data="no_flowers")])
    else:
        for flower in flowers:
            row.append(types.InlineKeyboardButton(text=flower[1], callback_data=f"flower_{flower[0]}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
    buttons.append([types.InlineKeyboardButton(text="Назад", callback_data="catalog")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_keyboard(category_id):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Заказываем!", callback_data="order")],
            [types.InlineKeyboardButton(text="Посмотрим другие", callback_data=f"back_{category_id}")]
        ]
    )
