from aiogram import Dispatcher, types

from handlers.keyboards import keyboard
from database import bot_db


async def process_start_command(message: types.Message):
    await message.reply("Приветствуем вас в дайвинчике УИТМЛ!\nЗарегестрируйтесь и находите себе друзей", reply_markup=keyboard)


async def process_help_command(message: types.Message):
    await message.reply("Напишите моему созадателю:\n@batyrhan221\nОн точно поможет (:", reply_markup=keyboard)


async def show_random_user(message: types.Message):
    await bot_db.sql_command_random(message)



def register_hendlers_client(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=["start"])
    dp.register_message_handler(process_help_command, commands=["help"])
    dp.register_message_handler(show_random_user,  lambda message: message.text == "Смотреть анкеты")