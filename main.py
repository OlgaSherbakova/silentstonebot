import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@mysilentchannel"  # Имя твоего канала (публичного)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем список заданий из файла
def load_tasks():
    with open("tasks.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

TASKS = load_tasks()

# Клавиатура с кнопками
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(
    KeyboardButton("📩 Отправить след"),
    KeyboardButton("🔁 Дай другое задание")
)

# /start — приветствие + первое задание
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    greeting = (
        "Привет. Я рад тебя видеть.\n\n"
        "Мне кажется, каждый человек — это уже искусство.\n\n"
        "Не знаю, считаешь ли ты себя искусством, \n"
        "но если хочешь — ниже будет задание, которое выпало случайно.\n\n"
        "Если хочешь — выполни.\n"
        "Если не хочешь — можешь просто отправить свой след: текст, фото, звук, ничего.\n\n"
        "Всё останется анонимным."
    )
    await message.answer(greeting, reply_markup=reply_kb)
    await send_task(message)

# 🔁 Дай другое задание — без приветствия
@dp.message_handler(lambda m: m.text == "🔁 Дай другое задание")
async def another_task(message: types.Message):
    await send_task(message)

# 📤 Функция отправки случайного задания
async def send_task(message):
    task = random.choice(TASKS)
    await message.answer(f"🎲 *Задание:* {task}", parse_mode="Markdown")

# 📩 Пользователь хочет отправить след
@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.")

# 📥 Обработка любого полученного отклика и публикация в канал
@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_trace(message: types.Message):
    await message.answer("Спасибо. След получен. Возвращайся, когда захочешь новое задание 🌿")

    try:
        if message.text:
            await bot.send_message(CHANNEL_ID, f"📝 След от пользователя:\n\n{message.text}")
        elif message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption="📸 След (фото)")
        elif message.voice:
            await bot.send_voice(CHANNEL_ID, message.voice.file_id, caption="🎤 След (голос)")
        elif message.audio:
            await bot.send_audio(CHANNEL_ID, message.audio.file_id, caption="🎵 След (аудио)")
        elif message.document:
            await bot.send_document(CHANNEL_ID, message.document.file_id, caption="📎 След (файл)")
        else:
            await bot.send_message(CHANNEL_ID, "📦 След получен (неопознанный тип)")
    except Exception as e:
        print("Ошибка при отправке в канал:", e)

# 🔁 Запуск бота
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
