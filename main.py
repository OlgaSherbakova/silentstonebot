import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем задания
def load_tasks():
    with open("tasks.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

TASKS = load_tasks()

# Клавиатура
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(
    KeyboardButton("📩 Отправить след"),
    KeyboardButton("🔁 Дай другое задание")
)

# Только при /start — приветствие
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
    await send_task(message)  # сразу после приветствия — задание

# При повторной просьбе → только задание
@dp.message_handler(lambda m: m.text == "🔁 Дай другое задание")
async def another_task(message: types.Message):
    await send_task(message)

# Общая функция для выдачи задания
async def send_task(message):
    task = random.choice(TASKS)
    await message.answer(f"🎲 *Задание:* {task}", parse_mode="Markdown")

# Отклик от пользователя
@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.")

@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_trace(message: types.Message):
    await message.answer("Спасибо. След получен. Возвращайся, когда захочешь новое задание 🌿")

# Запуск
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
