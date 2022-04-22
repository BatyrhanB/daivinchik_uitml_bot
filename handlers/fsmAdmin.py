from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.keyboards import cancel_markup, keyboard
from config import bot, ADMIN , dp
from database import bot_db


class AnketaFSM(StatesGroup):
    photo = State()
    name = State()
    surname = State()
    age = State()
    gender = State()
    description = State()
    school = State()
    


async def fsm_start(message: types.Message):
    if message.chat.type == 'private':
        await AnketaFSM.photo.set()
        await bot.send_message(message.chat.id,
                               f"Привет {message.from_user.full_name}, скинь фотку, его будут видеть другие пользователи",
                               reply_markup=cancel_markup)
    else:
        await message.answer("В личку мне пиши!")


async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.from_user.id
        data['nickname'] = f"@{message.from_user.username}"
        data['photo'] = message.photo[0].file_id
    await AnketaFSM.next()
    await bot.send_message(message.chat.id, "Как мне тебя называть?")


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await AnketaFSM.next()
    await bot.send_message(message.chat.id, "Какая фамилия?")


async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await AnketaFSM.next()
    await bot.send_message(message.chat.id, "Сколько тебе лет?")


async def process_age(message: types.Message, state: FSMContext):
    await AnketaFSM.next()
    await state.update_data(age=int(message.text))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add("Парень", "Девушка")
    await message.reply("Теперь определимся с полом", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Парень", "Девушка"], state=AnketaFSM.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Нету такого варианта.")



async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await AnketaFSM.next()
    await bot.send_message(message.chat.id, "Где учишься?")


async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await AnketaFSM.next()
    await bot.send_message(message.chat.id, "Расскажи о себе, кого хочешь найти, чем предлагаешь заняться")


async def process_school(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['school'] = message.text
    await bot_db.sql_command_insert(state)
    await state.finish()
    markup = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, "Так выглядит твоя анкета:")
    await bot_db.sql_command_myanketa(message)
    results = await bot_db.sql_command_myanketa(message)
    for result in results:
        await bot.send_photo(message.from_user.id, result[2],
                                caption=f"{result[3]} {result[4]}, {result[5]}, {result[6]}\n"
                                 f"school: {result[7]}\n\n"
                                 f"{result[1]}", reply_markup=keyboard)


async def cancal_reg(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    else:
        await state.finish()
        await message.reply("ОК", reply_markup=keyboard)


async def delete_data(message: types.Message):
    if message.from_user.id == ADMIN:
        results = await bot_db.sql_command_all(message)
        for result in results:
            await bot.send_photo(message.from_user.id, result[2],
                                 caption=f"Name: {result[3]}\n"
                                         f"Surname: {result[4]}\n"
                                         f"Age: {result[5]}\n"
                                         f"Gender: {result[6]}\n"
                                         f"School: {result[7]}\n\n"
                                         f"{result[1]}",
                                 reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                                     f"delete: {result[3]}",
                                     callback_data=f"delete: {result[0]}"
                                 )))
    else:
        await message.answer("Ты не админ!!!")


async def delete_mydata(message: types.Message):
        results = await bot_db.sql_command_all(message)
        for result in results:
            await bot.send_photo(message.from_user.id, result[2],
                                 caption=f"{result[3]} {result[4]}, {result[5]}, – "
                                 f"{result[8]}\n\n"
                                 f"{result[1]}",
                                 reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                                     f"Удалить анкету: {result[3]}",
                                     callback_data=f"delete: {result[0]}"
                                 )))


async def complete_delete(call: types.CallbackQuery):
    await bot_db.sql_command_delete(call.data.replace('delete: ', ''))
    await call.answer(text=f"{call.data.replace('delete: ', '')} deleted", show_alert=True)
    await bot.delete_message(call.message.chat.id, call.message.message_id)





def register_hendler_fsmAdminGetUser(dp: Dispatcher):
    dp.register_message_handler(cancal_reg, state="*", commands="cancel")
    dp.register_message_handler(cancal_reg, Text(equals='cancel', ignore_case=True), state="*")

    dp.register_message_handler(fsm_start, lambda message: message.text == "Регистрация")
    dp.register_message_handler(process_photo, state=AnketaFSM.photo, content_types=["photo"])
    dp.register_message_handler(process_name, state=AnketaFSM.name)
    dp.register_message_handler(process_surname, state=AnketaFSM.surname)
    dp.register_message_handler(process_age, state=AnketaFSM.age)
    dp.register_message_handler(process_gender, state=AnketaFSM.gender)
    dp.register_message_handler(load_description, state=AnketaFSM.description)
    dp.register_message_handler(process_school, state=AnketaFSM.school)

    dp.register_message_handler(delete_data, commands=['delete'])
    dp.register_message_handler(delete_mydata, lambda message: message.text == "Удалить мою анкету")
    dp.register_callback_query_handler(complete_delete,
                                       lambda call: call.data and call.data.startswith("delete: "))