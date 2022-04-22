from aiogram import Bot, executor, Dispatcher, types
from config import dp
import logging

from handlers import client, fsmAdmin
from database import bot_db

async def on_start_up(_):
    bot_db.sql_create()

client.register_hendlers_client(dp)
fsmAdmin.register_hendler_fsmAdminGetUser(dp)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=False,  on_startup=on_start_up)