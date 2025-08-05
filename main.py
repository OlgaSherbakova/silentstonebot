import os
import requests
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Настройки
TOKEN = "8142905270:AAEK9RGFV1DZkrw7j-i3qFnimSKaw5XBIMc"
CHANNEL_ID = "@mysilentchannel"
WEBHOOK_HOST = 'https://<your-app-name>.railway.app'  # Замените на URL вашего приложения на Railway
WEBHOOK_PATH = '/webhook'  # Путь, на который Telegram будет отправлять обновления
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

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

# Функция для установки вебхука
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)

# Обработчик для /start
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

        # 🔘 Кнопка со ссылкой на канал
        channel_button = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📡 Перейти в канал", url="https://t.me/mysilentchannel")
        )
        await message.answer("📡 Следы появляются в канале:", reply_markup=channel_button)

# Обработчик для нового задания
@dp.message_handler(lambda m: m.text == "🔁 Дай другое задание")
async def another_task(message: types.Message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_last_task_date.get(user_id) == today:
        await message.answer("🕒 Сегодня ты уже получал задание. Приходи завтра.", reply_markup=reply_kb)
    else:
        await send_task(message)
        user_last_task_date[user_id] = today

# Функция для отправки задания
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

# Обработчик для отправки следа
@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.", reply_markup=reply_kb)

# Обработчик для получения следов
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

            await bot.send_message(CHANNEL_ID, f"📝 След от пользователя:\n\n{content}")

        elif message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption="📸 След (фото)")
        elif message.voice:
            await bot.send_voice(CHANNEL_ID, message.voice.file_id, caption="🎤 След (голос)")
        elif message.video:
            await bot.send_video(CHANNEL_ID, message.video.file_id, caption="🎬 След (видео)")
        elif message.video_note:
            await bot.send_video_note(CHANNEL_ID, message.video_note.file_id)
        elif message.sticker:
            await bot.send_sticker(CHANNEL_ID, message.sticker.file_id)
        elif message.audio:
            await bot.send_audio(CHANNEL_ID, message.audio.file_id, caption="🎵 След (аудио)")
        elif message.document:
            await bot.send_document(CHANNEL_ID, message.document.file_id, caption="📎 След (файл)")

    except Exception as e:
        print("Ошибка при отправке в канал:", e)

# Обработчик для вебхуков
async def on_webhook(request):
    json_str = await request.json()
    update = types.Update.parse_obj(json_str)
    await dp.process_update(update)
    return web.Response(text="OK")

# Основная функция для старта
async def main():
    # Устанавливаем вебхук
    await set_webhook()

    # Настроим веб-сервер для получения обновлений
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, on_webhook)
    app.router.add_get('/', lambda request: web.Response(text="Bot is working"))  # Просто тестовый эндпоинт
    web.run_app(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    asyncio.run(main())
