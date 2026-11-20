import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.client.telegram import TelegramAPIServer
import pyautogui
import keyboard
import webbrowser
import os
import time
import psutil
import subprocess
import pygetwindow
import tkinter as tk
import ctypes
import multiprocessing
import winsound
import threading
from PIL import Image
import io
import pyperclip
import pywin32_system32
import win32clipboard
from config import TOKEN, ADMIN_ID
bot = Bot(token=TOKEN)
dp = Dispatcher()
IS_WATCHING = False
FILE_FOUND_CACHE = {}



def get_pc_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть ютуб", callback_data="pc_youtube")],
            [InlineKeyboardButton(text="Открыть Lichess", callback_data="pc_lichess")],
            [InlineKeyboardButton(text="Скриншот", callback_data="pc_screen")],
            [InlineKeyboardButton(text="Открыть блокнот", callback_data="pc_notepad")],
            [InlineKeyboardButton(text="Скрыть все", callback_data="pc_minimize")],
        ]
    )


@dp.message(Command("start_pc"))
async def cmd_start_pc(message: types.Message):
    await message.answer(
        "Пульт управления активирован, выбери действие: ",
        reply_markup=get_pc_keyboard(),
    )


@dp.message(Command("site"))
async def cmd_open_site(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет доступа к этому ПК!")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Неправильный ввод! Пиши так: /site google.com")
        return
    url = parts[1]
    if "http" not in url:
        url = "https://" + url
    webbrowser.open(url)
    await message.answer(f"Открываю сайт {url} ")


@dp.message(Command("write"))
async def cmd_write(message: types.Message):
    if message.from_user.id != 1423879343:
        await message.answer("У тебя нет доступа к этому ПК!")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Неправильный ввод! Пиши так /write (текст)")
        return
    text = parts[1]
    await message.answer(f"Ввожу через 1 секунду: {text}. Открой блокнот!")
    await asyncio.sleep(1)
    keyboard.write(text, delay=0.05)


@dp.callback_query()
async def process_pc_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("У тебя нет доступа к этому ПК!")
        return
    data = callback_query.data
    if data.startswith("getfile_"):
        user_id = callback_query.from_user.id
        if user_id in FILE_FOUND_CACHE:
            file_index = int(data.split("_")[1])
            file_path = FILE_FOUND_CACHE[user_id][file_index]
            await callback_query.answer("Отправляю...")
            await send_file_to_user(user_id, file_path)
        else:
            await callback_query.answer("Список файлов устарел, используй /find заново")
        return
    if data.startswith("sounds_"):
        sound_type = data.replace("sounds_", "")
        if sound_type == "off":
            winsound.PlaySound(None, winsound.SND_PURGE)
            await callback_query.answer("Звук остановлен")
            return
        if sound_type == "siren":
            file_name = "military-siren.mp3--online-audio-convert.com.wav"
        elif sound_type == "lucky":
            file_name = "lucky-lucky.mp3--online-audio-convert.com.wav"
        elif sound_type == "penetration":
            file_name = "there-is-a-penetration.mp3--online-audio-convert.com.wav"
        elif sound_type == "screw":
            file_name = "from-screw-bass-bossted.mp3--online-audio-convert.com.wav"
        if os.path.exists(file_name):
            try:
                winsound.PlaySound(
                    file_name,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
                )
                await callback_query.answer(f"Включаю: {sound_type}!")
            except Exception as e:
                await callback_query.answer(f"❌ Ошибка: {e}")
        else:
            await callback_query.answer(f"❌Файл {file_name} не найден ")
        return
    elif data == "pc_youtube":
        webbrowser.open("https://www.youtube.com")
        await callback_query.answer("Браузер открыт!")
    elif data == "pc_lichess":
        webbrowser.open("https://lichess.org/")
        await callback_query.answer("Шахматы открыты!")
    elif data == "pc_screen":
        screenshot_path = "temp_screen.png"
        screenshot = pyautogui.screenshot(screenshot_path)

        img = Image.open(screenshot_path)

        output = io.BytesIO()
        img.convert("RGB").save(output, format="JPEG", quality=95)
        output.seek(0)

        photo = types.BufferedInputFile(output.read(), filename="screen.jpg")
        await callback_query.message.answer_photo(
            photo=photo, caption="Вот твой экран!"
        )
    elif data == "pc_minimize":
        keyboard.send("windows + d")
        await callback_query.answer("Все окна скрыты!")
    elif data == "pc_notepad":
        subprocess.Popen("notepad", shell=True)
        await callback_query.answer(f"Запускаю блокнот!")
    elif data == "vol_up":
        for _ in range(5):
            pyautogui.press("volumeup")
        await callback_query.answer("Громкость добавлена")
        return
    elif data == "vol_down":
        for _ in range(5):
            pyautogui.press("volumedown")
        await callback_query.answer("Громкость убавлена")
        return
    elif data == "vol_mute":
        pyautogui.press("volumemute")
        await callback_query.answer("Звук выключен(или включен)!")
        return

    print(f"debug: data = {data}")


@dp.message(Command("ls"))
async def cmd_list_files(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Отказано в доступе")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        path = "."
    else:
        path = parts[1]
    try:
        items = os.listdir(path)
        if not items:
            message.answer(f"Папка {path} пуста")
            return
        result_text = f"Содержимое папки `{path}`: \n\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result_text += f"📁 {item} /\n"
            else:
                result_text += f"📄 {item} /\n"
        await message.answer(f"```\n{result_text[:4000]}\n```", parse_mode="MarkdownV2")
    except FileNotFoundError:
        await message.answer("Нет такой папки, проверь путь")
    except PermissionError:
        await message.answer("Нет доступа к папке(системная папка)")


@dp.message(Command("get"))
async def cmd_get_file(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Напиши так: /get C:\\путь\\к\\файлу.txt")
        return
    file_path = parts[1]
    if not os.path.isfile(file_path):
        await message.answer("❌ Файл не найден. Проверь путь")
        return
    try:
        await message.answer("📩 Отправляю файл")
        file_to_send = FSInputFile(file_path)
        await message.answer_document(document=file_to_send)
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке: {e}")


@dp.message(Command("tasks"))
async def cmd_show_tasks(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    await message.answer("Собираю список процессов")
    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                mem_mb = proc.info["memory_info"].rss / (1024 * 1024)
                processes.append(
                    (
                        mem_mb,
                        proc.info["pid"],
                        proc.info["name"],
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        processes.sort(key=lambda x: x[0], reverse=True)
        result_text = f"**Топ-15 процессов:**\n\n"
        for mem_mb, pid, name in processes[:15]:
            result_text += f"[{pid}] {name} - {mem_mb:.1f} MB\n"
        await message.answer(result_text)

    except Exception as e:
        await message.answer(f"❌Ошибка: {e}")


@dp.message(Command("kill"))
async def cmd_kill_task(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Напиши так: /kill notepad.exe или /1234 (где 1234 - это PID)"
        )
        return
    target = parts[1].strip()
    killed = False
    try:
        if target.isdigit():
            pid = int(target)
            process = psutil.Process(pid)
            process.terminate()
            await message.answer(f"Процесс с PID - {pid }({process.name()}) убит")
        else:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and proc.info["name"].lower() == target.lower():
                    proc.terminate()
                    killed = True
        if killed:
            await message.answer(f"Все процессы {target} убиты")
        else:
            await message.answer(f"❌ Процесс {target} не найден")
    except psutil.NoSuchProcess:
        await message.answer("Процесс уже закрыт или не существует")
    except psutil.AccessDenied:
        await message.answer(
            "❌ Отказано в доступе, запусти программу через администратора"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("run"))
async def cmd_run_programm(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пиши так: /run notepad.exe(или путь к файлу)")
        return
    programm = parts[1].split()
    try:
        subprocess.Popen(programm, shell=True)
        await message.answer(f"Запускаю: {programm}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("watch_on"))
async def cmd_watch_on(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    global IS_WATCHING
    if IS_WATCHING:
        await message.answer("👁️ Охрана уже включена")
        return
    IS_WATCHING = True
    await message.answer(
        "👁️ Режим охраны ВКЛЮЧЕН. Я буду присылать тебе сообщения о изменениях!"
    )
    asyncio.create_task(watch_window_loop(message.chat.id))


@dp.message(Command("watch_off"))
async def cmd_watch_off(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    global IS_WATCHING
    IS_WATCHING = False
    await message.answer("👁️ Режим охраны ВЫКЛЮЧЕН.")


async def watch_window_loop(chat_id):
    global IS_WATCHING
    last_window = ""
    while IS_WATCHING:
        try:
            active_window = pygetwindow.getActiveWindow()
            if active_window is not None and active_window.title:
                current_title = active_window.title
            if current_title != last_window:
                if last_window != "":
                    pyautogui.screenshot("watch_screen.png")
                    photo = types.FSInputFile("watch_screen.png")
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=f"👁️ Смена окна: {current_title}",
                    )
                last_window = current_title
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Для консоли: Ошибка при чтении окна: {e}")
            await asyncio.sleep(5)


async def send_file_to_user(chat_id, file_path, message_to_edit=None):
    if not os.path.isfile(file_path):
        await bot.send_message(chat_id=chat_id, text="❌ Файл не найден")
        return
    try:
        await bot.send_message(chat_id=chat_id, text="📩 Отправляю файл...")
        file_to_send = FSInputFile(file_path)
        await bot.send_document(chat_id=chat_id, document=file_to_send)
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Ошибка: {e}")


@dp.message(Command("blackout"))
async def cmd_blackout(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    await message.answer("Монитор выключен")
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)


@dp.message(Command("find"))
async def cmd_find(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пиши так: /find имя_файла (например /find отчет)")
        return
    search_query = parts[1].strip().lower()
    await message.answer(f'🔎 Ищу "{search_query}" это может занять время...')
    found_files = []
    search_paths = [
        "C:\\Users\\User\\Desktop",
        "C:\\Users\\User\\Downloads",
        "C:\\Users\\User\\Documents",
        "C:\\MyPythonProjects",
        "C:\\Games\\chessbase данные",
        "F:\\рабочий стол\\фото",
    ]
    try:
        for base_path in search_paths:
            if os.path.exists(base_path):
                for (
                    root,
                    dirs,
                    files,
                ) in os.walk(base_path):
                    for file in files:
                        if search_query in file.lower():
                            full_path = os.path.join(root, file)
                            found_files.append(full_path)

                            if len(found_files) >= 10:
                                break
                    if len(found_files) >= 10:
                        break
                if len(found_files) >= 10:
                    break
        if not found_files:
            await message.answer(f"❌ Файл с именем {search_query} не найден")
        else:
            user_id = message.from_user.id
            FILE_FOUND_CACHE[user_id] = found_files
            keyboard_buttons = []
            for i, file_path in enumerate(found_files):
                file_name = os.path.basename(file_path)
                if len(file_name) > 30:
                    file_name = file_name[:27] + "..."

                keyboard_buttons.append(
                    [InlineKeyboardButton(text=file_name, callback_data=f"getfile_{i}")]
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

                result_text = f"📁 **Найдено {len(found_files)} файлов (макс. 10). Выбери что скачать: **\n\n "
                for path in found_files:
                    result_text += f"`{path}`\n\n"
            await message.answer(result_text, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("sounds"))
async def cmd_sounds(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сирена", callback_data="sounds_siren")],
            [
                InlineKeyboardButton(
                    text="О повезло, повезло", callback_data="sounds_lucky"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Есть пробитие", callback_data="sounds_penetration"
                )
            ],
            [InlineKeyboardButton(text="От винта", callback_data="sounds_screw")],
            [InlineKeyboardButton(text="Остановить все", callback_data="sounds_off")],
        ]
    )
    await message.answer("Выбери, что включить на компьюетере:", reply_markup=keyboard)


@dp.message(Command("volume"))
async def cmd_volume(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔊 Громче", callback_data="vol_up"),
                InlineKeyboardButton(text="🔈 Тише", callback_data="vol_down"),
            ],
            [InlineKeyboardButton(text="🔇 Выключить звук", callback_data="vol_mute")],
        ]
    )
    await message.answer("Управление громкостью:", reply_markup=keyboard)


@dp.message(Command("message"))
async def cmd_show_message(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пиши так: /message бла-бла-бла")
        return
    text = parts[1]
    try:
        threading.Thread(
            target=ctypes.windll.user32.MessageBoxW, args=(0, text, "Сообщение", 0x40)
        ).start()
        await message.answer(f"Отправляю сообщение {text}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

def copy_image_to_clipboard(image_bytes: bytes):
    image = image.open(io.BytesIO(image_bytes))
    output = io.BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData()
    win32clipboard.CloseClipboard()
@dp.message(Command('clip_get'))
async def cmd_clip_get(message:types.Message):
    if message.from_user.id != ADMIN_ID:
            await message.answer("❌ Доступ запрещен ❌")
            return
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            text= win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            await message.answer(f'Текст с ПК: \n\n{text}')
        else:
            await message.answer(f'Буфер обмена пуст')
    except Exception as e:
        await message.answer(f'❌ Ошибка: {e}')

    finally:
        win32clipboard.CloseClipboard()

@dp.message(Command('clip_set'))
async def cmd_clip_set(message:types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен ❌")
        return
    if message.reply_to_message and message.reply_to_message.text:
        text_to_copy = message.reply_to_message.text
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer('Пиши так: /clip_set Твой текст')
            return
        text_to_copy = parts[1]
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text_to_copy, win32clipboard.CF_UNICODETEXT)
        await message.answer(f'Скопировано на ПК: \n\n{text_to_copy[:100]}...')
    except Exception as e:
        await message.answer(f'❌ Ошибка: {e}')
    finally:
        win32clipboard.CloseClipboard()
async def main():
    print("Пульт управления запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
