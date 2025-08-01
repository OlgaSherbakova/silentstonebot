import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

# Токен бота — уже вписан
TOKEN = "8142905270:AAEK9RGFV1DZkrw7j-i3qFnimSKaw5XBIMc"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем список заданий
def load_tasks():
    with open("tasks.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

TASKS = load_tasks()

# Кнопка "Отправить след"
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(KeyboardButton("📩 Отправить след"))

@dp.message_handler(commands=["start"])
async def welcome(message: types.Message):
    task = random.choice(TASKS)
    text = (
        "Привет. Я рад тебя видеть.\n\n"
        "Мне кажется, каждый человек — это уже искусство.\n\n"
        "Не знаю, считаешь ли ты себя искусством, \n"
        "но если хочешь — ниже будет задание, которое выпало случайно.\n\n"
        f"🎲 *Задание:* {task}\n\n"
        "Если хочешь — выполни.\n"
        "Если не хочешь — можешь просто отправить свой след: текст, фото, звук, ничего.\n\n"
        "Всё останется анонимным."
    )
    await message.answer(text, reply_markup=reply_kb, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.")

@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_trace(message: types.Message):
    await message.answer("Спасибо. След получен. Возвращайся, когда захочешь новое задание 🌿")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
