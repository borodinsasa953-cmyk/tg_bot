import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyautogui
import  keyboard
import webbrowser
import os
import time
from config import TOKEN
PROXY_URL = 'http://127.0.0.1:12334'
session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=TOKEN, session=session)
dp =  Dispatcher()
def get_pc_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Открыть ютуб', callback_data='pc_youtube')],
        [InlineKeyboardButton(text='Открыть Lichess',callback_data='pc_lichess')],
        [InlineKeyboardButton(text='Напечатать текст',callback_data='pc_text')],
        [InlineKeyboardButton(text='Скриншот', callback_data='pc_screen')],
        [InlineKeyboardButton(text='Скрыть все', callback_data='pc_minimize')]
    ])
@dp.message(Command('start_pc'))
async def cmd_start_pc(message:types.Message):
    await message.answer('Пульт управления активирован, выбери действие: ',reply_markup=get_pc_keyboard())
@dp.message(Command('site'))
async def cmd_open_site(message:types.Message):
    if message.from_user.id != 1423879343:
        await message.answer('У тебя нет доступа к этому ПК!')
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Неправильный ввод! Пиши так: /site google.com')
        return
    url = parts[1]
    if 'http' not in url:
        url = 'https://' + url
    webbrowser.open(url)
    await message.answer(f'Открываю сайт {url} ')
@dp.message(Command('write'))
async def cmd_write(message:types.Message):
    if message.from_user.id != 1423879343:
            await message.answer('У тебя нет доступа к этому ПК!')
            return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Неправильный ввод! Пиши так /write (текст)')
        return
    text = parts[1]
    await message.answer(f'Ввожу через 2 секунды: {text}. Открой блокнот!')
    await asyncio.sleep(2)
    pyautogui.write(text, interval=0.05)
@dp.callback_query()
async def process_pc_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != 1423879343:
        await callback_query.answer('У тебя нет доступа к этому ПК!')
        return
    data = callback_query.data
    if data == 'pc_youtube':
        webbrowser.open('https://www.youtube.com')
        await callback_query.answer('Браузер открыт!')
    elif data == 'pc_lichess':
        webbrowser.open('https://lichess.org/')
        await callback_query.answer('Шахматы открыты!')
    elif data =='pc_text':
        await callback_query.answer('Печатаю через 2 секунды. Переключись в блокнот!')
        await asyncio.sleep(2)
        pyautogui.write('Привет! Это управляется через Telegram!', interval=0.05)
    elif data =='pc_screen':
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        photo = types.FSInputFile('screenshot.png')
        await callback_query.message.answer_photo(photo=photo, caption='Вот твой экран!')
    elif data == 'pc_minimize':
        keyboard.send('windows + d')
        await callback_query.answer('Все окна скрыты!')
async def main():
    print('Пульт управления запущен!')
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())