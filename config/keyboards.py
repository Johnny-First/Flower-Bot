from aiogram import types

def get_base_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            # [types.KeyboardButton(text="Наш сайт")],
            # [types.KeyboardButton(text="О магазине")],
            [types.KeyboardButton(text="Заказать цветы")]
        ],
        resize_keyboard=True
    )

def get_flowers_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Розы", callback_data="rose"),
                types.InlineKeyboardButton(text="Пионы", callback_data="pion")
            ],
            [
                types.InlineKeyboardButton(text="Незабудки", callback_data="nezabudka"),
                types.InlineKeyboardButton(text="Другие цветы", callback_data="others")
            ]            
        ]
    )

def get_order_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Заказываем!", callback_data="order"),
            ],
            [
                types.InlineKeyboardButton(text="Посмотрим другие", callback_data="back"),
            ]
        ])
