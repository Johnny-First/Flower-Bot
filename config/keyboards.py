from aiogram import types
import sqlite3

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

def get_flowers_keyboard():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''FROM flowers ''')
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
