from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types


cancel_button = KeyboardButton("CANCEL")
cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

cancel_markup.add(cancel_button)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
buttons = ["Регистрация", "Смотреть анкеты", "Удалить мою анкету"]
keyboard.row(*buttons)