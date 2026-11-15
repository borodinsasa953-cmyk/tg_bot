import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from config import TOKEN
import random
PROXY_URL = 'http://127.0.0.1:12334'
calc_data = {}
session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=TOKEN, session=session)
dp =  Dispatcher()
def get_calc_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
    [
            InlineKeyboardButton(text='1', callback_data='num_1'),
            InlineKeyboardButton(text='2', callback_data='num_2'),
            InlineKeyboardButton(text='3', callback_data='num_3')

        ],
        [
            InlineKeyboardButton(text='4', callback_data='num_4'),
            InlineKeyboardButton(text='5', callback_data='num_5'),
            InlineKeyboardButton(text='6', callback_data='num_6')

        ],
        [
            InlineKeyboardButton(text='7', callback_data='num_7'),
            InlineKeyboardButton(text='8', callback_data='num_8'),
            InlineKeyboardButton(text='9', callback_data='num_9')
        ],
        [
            InlineKeyboardButton(text='0', callback_data='num_0'),
            InlineKeyboardButton(text='+', callback_data='op_add'),
            InlineKeyboardButton(text='*', callback_data='op_mul')

        ],
        [
            InlineKeyboardButton(text='/', callback_data='op_del'),
            InlineKeyboardButton(text='-', callback_data='op_min'),
            InlineKeyboardButton(text='=', callback_data='calc_equals')
        ],
        [
            InlineKeyboardButton(text='C', callback_data='clear')
        ]
        
    ])
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я твой первый бот. Напиши что-нибудь')
@dp.message(Command('whoisroma'))
async def cmd_whoisroma(message: types.Message):
    list = ['Лошара-петушара', 'Крутой пацан', "лошок", 'нормальный человек', 'балбес', 'просто рома', 'дебил', 'бог', 'нуб', 'говно', 'ровный пацан', 'петух']
    roma = random.choice(list)
    await  message.answer(f'Рома - {roma}')

@dp.message(Command('calc'))
async def cmd_calc(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='1', callback_data='num_1'),
            InlineKeyboardButton(text='2', callback_data='num_2'),
            InlineKeyboardButton(text='3', callback_data='num_3')

        ],
        [
            InlineKeyboardButton(text='4', callback_data='num_4'),
            InlineKeyboardButton(text='5', callback_data='num_5'),
            InlineKeyboardButton(text='6', callback_data='num_6')

        ],
        [
            InlineKeyboardButton(text='7', callback_data='num_7'),
            InlineKeyboardButton(text='8', callback_data='num_8'),
            InlineKeyboardButton(text='9', callback_data='num_9')
        ],
        [
            InlineKeyboardButton(text='0', callback_data='num_0'),
            InlineKeyboardButton(text='+', callback_data='op_add'),
            InlineKeyboardButton(text='*', callback_data='op_mul')

        ],
        [
            InlineKeyboardButton(text='/', callback_data='op_del'),
            InlineKeyboardButton(text='-', callback_data='op_min'),
            InlineKeyboardButton(text='=', callback_data='calc_equals')
        ],
        [
            InlineKeyboardButton(text='C', callback_data='clear')
        ]

    ])
    await message.answer('Введи первое число,потом операцию, потом второе число и нажми "="', reply_markup=keyboard)
@dp.callback_query()  
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    

    if user_id not in calc_data:
        calc_data[user_id] = {"current": "", "first": "", "op": ""}
    user_calc = calc_data[user_id]


    if data.startswith("num_"):
        num = data.split("_")[1]
        user_calc["current"] += num
        

        if user_calc["op"] == "":

            text = f"Введено: {user_calc['current']}\nВыбери операцию."
        else:

            op_sym = {"op_add": "+", "op_min": "-", "op_mul": "*", "op_del": "/"}[user_calc["op"]]
            text = f"{user_calc['first']} {op_sym} {user_calc['current']}\nНажми = для результата."
            
        await callback_query.message.edit_text(text, reply_markup=get_calc_keyboard())


    elif data in ["op_add", "op_min", "op_mul", "op_del"]:
        if user_calc["current"] == "" and user_calc["first"] == "":
            await callback_query.answer("Сначала введи число!")
            return
        
        if user_calc["op"] == "":
            user_calc["first"] = user_calc["current"]
            user_calc["current"] = ""
            user_calc["op"] = data
        else:

            user_calc["op"] = data
            
        op_sym = {"op_add": "+", "op_min": "-", "op_mul": "*", "op_del": "/"}[data]
        await callback_query.message.edit_text(
            f"{user_calc['first']} {op_sym} ...\nВведи второе число.",
            reply_markup=get_calc_keyboard()
        )


    elif data == "calc_equals":
        if user_calc["first"] == "" or user_calc["current"] == "":
            await callback_query.answer("Нужно ввести оба числа и операцию!")
            return
        
        num1 = int(user_calc["first"])
        num2 = int(user_calc["current"])
        op = user_calc["op"]
        
        if op == "op_add": result = num1 + num2
        elif op == "op_min": result = num1 - num2
        elif op == "op_mul": result = num1 * num2
        elif op == "op_del": 
            if num2 == 0: result = "Ошибка (деление на 0)"
            else: result = num1 / num2
            
        op_sym = {"op_add": "+", "op_min": "-", "op_mul": "*", "op_del": "/"}[op]
        await callback_query.message.edit_text(
            f"Результат: {num1} {op_sym} {num2} = {result}",
            reply_markup=get_calc_keyboard()
        )

        calc_data[user_id] = {"current": "", "first": "", "op": ""}


    elif data == "clear":
        calc_data[user_id] = {"current": "", "first": "", "op": ""}
        try:
            await callback_query.message.edit_text("Введи первое число.", reply_markup=get_calc_keyboard())
        except Exception:
            pass 


    await callback_query.answer()

        

    
@dp.message()
async def echo_handler(message:types.Message):
    await message.answer(f'Ты написал: {message.text}')
async def main():
    print('Бот запущен.')
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())