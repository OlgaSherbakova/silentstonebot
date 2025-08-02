
import random
import asyncio
import datetime
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Настройки
TOKEN = "8142905270:AAEK9RGFV1DZkrw7j-i3qFnimSKaw5XBIMc"
CHANNEL_ID = "@mysilentchannel"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем задания из файла
def load_tasks():
    with open("tasks.json", encoding="utf-8") as f:
        return json.load(f)

# Память: кто получал задание сегодня
user_last_task_date = {}

# История полученных заданий
user_task_history = {}  # user_id: set of task indexes

# Клавиатура
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(
    KeyboardButton("📩 Отправить след"),
    KeyboardButton("🔁 Дай другое задание")
)

# Фильтры
BAD_WORDS = [
    "хуй", "член", "пенис", "еб", "пизд", "fuck", "shit",
    "dick", "порно", "трах", "дроч", "anal", "cum", "педофил"
]
LITE_SWEAR = ["бля", "сука", "нахуй", "ебать", "пиздец"]
JUNK_WORDS = [
    "старт", "start", "ага", "ну", "да", "нет", "ок", "okay", "hello", "привет",
    "ещё", "еще", "следующее задание", "другое задание", "дай другое", "повтори",
    "ещё раз", "next", "again", "задание", "ещё!", "ещё.", "ещё?", "ещё)"
]

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    today = datetime.date.today()
    last_date = user_last_task_date.get(user_id)

    greeting = """Привет. Я рад тебя видеть.

Этот бот — про спонтанное творчество. Он даёт случайные задания: иногда простые, иногда странные, иногда почти ничего.

Всё остаётся анонимным. Здесь никто не проверяет, не оценивает, не ждёт результата.

Мне кажется, каждый человек — это уже искусство.

Не знаю, считаешь ли ты себя искусством, 
но если хочешь — ниже будет задание, которое выпало случайно.

Можно выполнить. Можно не выполнять. Можно просто отправить след: текст, фото, звук.

Это пространство — открытое. 
Можно делать как хочешь. Ради действия. Ради игры. Ради того, чтобы просто попробовать."""
    await message.answer(greeting, reply_markup=reply_kb)

    if last_date == today:
        await message.answer("🕒 Сегодня ты уже получал задание. Приходи завтра.", reply_markup=reply_kb)
    else:
        await send_task(message)
        user_last_task_date[user_id] = today
        await message.answer("📡 Следы появляются в канале:\nhttps://t.me/mysilentchannel", reply_markup=reply_kb)

@dp.message_handler(lambda m: m.text == "🔁 Дай другое задание")
async def another_task(message: types.Message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_last_task_date.get(user_id) == today:
        await message.answer("🕒 Сегодня ты уже получал задание. Приходи завтра.", reply_markup=reply_kb)
    else:
        await send_task(message)
        user_last_task_date[user_id] = today

async def send_task(message):
    user_id = message.from_user.id
    tasks = load_tasks()
    total = len(tasks)

    history = user_task_history.get(user_id, set())
    available = [i for i in range(total) if i not in history]

    if not available:
        await message.answer("🎉 Ты прошёл все задания! Завтра можно будет начать заново.", reply_markup=reply_kb)
        user_task_history[user_id] = set()
        return

    task_index = random.choice(available)
    task = tasks[task_index]

    history.add(task_index)
    user_task_history[user_id] = history

    await message.answer(f"*{task['title']}*\n\n{task['description']}", parse_mode="Markdown", reply_markup=reply_kb)

@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.", reply_markup=reply_kb)

@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_trace(message: types.Message):
    await message.answer("Спасибо. След получен. Возвращайся, когда захочешь новое задание 🌿", reply_markup=reply_kb)

    try:
        if message.text:
            content = message.text.strip()
            lower = content.lower()

            if any(junk in lower for junk in JUNK_WORDS) or len(content) <= 2:
                print("⚠️ Мусорное сообщение — не публикуется")
                return

            if any(word in lower for word in BAD_WORDS):
                print("❌ Заблокировано из-за жёстких слов")
                return

            if len(content.split()) <= 3 and any(word in lower for word in LITE_SWEAR):
                print("⚠️ Короткий мат — не публикуется")
                return

            await bot.send_message(CHANNEL_ID, f"📝 След от пользователя:

{content}")

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

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
