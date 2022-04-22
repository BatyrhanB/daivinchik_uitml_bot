import sqlite3
import random
from aiogram import types

from config import bot


def sql_create():
    global db, cursor
    db = sqlite3.connect("bot.sqlite3")
    cursor = db.cursor()
    if db:
        print("База данных подключена!")
    db.execute("CREATE TABLE IF NOT EXISTS anketa"
               "(id INTEGER PRIMARY KEY, nickname TEXT, photo TEXT, "
               "name TEXT, surname TEXT, age INTEGER, gender TEXT, description TEXT, school TEXT)")
    db.commit()


async def sql_command_insert(state):
    async with state.proxy() as data:
        cursor.execute("INSERT OR IGNORE INTO anketa VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(data.values()))
        db.commit()


async def sql_command_random(message):
    result = cursor.execute("SELECT * FROM anketa").fetchall()
    r_u = random.randint(0, len(result)-1)
    await bot.send_photo(message.from_user.id, result[r_u][2],
                         caption=f"{result[r_u][3]} {result[r_u][4]}, {result[r_u][5]}, – "
                                 f"{result[r_u][8]}\n\n"
                                 f"{result[r_u][1]}")


async def sql_command_all(message):
    return cursor.execute("SELECT * FROM anketa").fetchall()


async def sql_command_delete(id):
    cursor.execute("DELETE FROM anketa WHERE id == ?", (id,))
    db.commit()


async def sql_command_myanketa(message: types.Message):
    return cursor.execute("SELECT * FROM anketa WHERE id = ?", (message.from_user.id,)).fetchall()


async def sql_command_all(message):
    return cursor.execute("SELECT * FROM anketa WHERE id = ?", (message.from_user.id,)).fetchall()
