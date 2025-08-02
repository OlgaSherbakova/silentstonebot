import random
import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

# Бот и канал
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@mysilentchannel"
CHANNEL_LINK = "https://t.me/mysilentchannel"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Расширенные задания
expanded_tasks = [
    {
        "title": "🌀 Стань пакетом.",
        "description": "Представь, что ты — обычный пластиковый пакет.\n\nГде ты сейчас? На ветру? В шкафу? В чьей руке?\n\nЧто ты чувствуешь? Обиду, свободу, тоску, гордость, пустоту?\n\nВырази это как хочешь: 📷 фото, 📝 текст, 🎥 видео, 🎨 рисунок — или просто подумай об этом пару минут."
    },
    {
        "title": "🎨 Один цвет.",
        "description": "Выбери любой цвет. Найди 3–5 предметов этого цвета вокруг себя.\n\nРазложи их. Присмотрись. Это может быть рассказ? Настроение? Картина?\n\nМожешь сфотографировать, нарисовать, описать — или просто посмотреть."
    },
    {
        "title": "🕯️ Смотри на свечу.",
        "description": "Зажги свечу (или представь её). Смотри 5 минут. Не отвлекайся.\n\nПусть мысли текут. Потом — запиши или нарисуй всё, что пришло в голову."
    },
    {
        "title": "📦 Натюрморт с улицы.",
        "description": "Найди 5 случайных предметов на улице. Любых. Упавший лист, камень, крышка, палка…\n\nСобери из них натюрморт. Как он выглядит? Что в нём странного или прекрасного?\n\nСфотографируй или просто выложи на минуту и разгляди."
    },
    {
        "title": "💬 Разговор между вилками.",
        "description": "Представь, что две вилки обсуждают что-то важное. Что между ними? Любовь? Спор? Зависть?\n\nНапиши их диалог. Или разыграй сценку. Или выложи их в позах. Или просто услышь этот разговор в голове."
    }
]

# Память: кто уже получил задание сегодня
user_last_task_date = {}

# Клавиатура
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(
    KeyboardButton("📩 Отправить след"),
    KeyboardButton("🔁 Дай другое задание")
)

# Фильтры
BAD_WORDS = ["хуй", "член", "пенис", "еб", "пизд", "fuck", "shit", "dick", "порно", "трах", "дроч", "anal", "cum", "педофил"]
LITE_SWEAR = ["бля", "сука", "нахуй", "ебать", "пиздец"]
JUNK_WORDS = ["старт", "start", "ага", "ну", "да", "нет", "ок", "hello", "привет"]

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    today = datetime.date.today()
    last_date = user_last_task_date.get(user_id)

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

    if last_date == today:
        await message.answer("🕒 Сегодня ты уже получал задание. Приходи завтра.")
    else:
        await send_task(message)
        user_last_task_date[user_id] = today
        await message.answer(f"📡 Следы появляются в канале:\n{CHANNEL_LINK}")

@dp.message_handler(lambda m: m.text == "🔁 Дай другое задание")
async def another_task(message: types.Message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_last_task_date.get(user_id) == today:
        await message.answer("🕒 Сегодня ты уже получал задание. Приходи завтра.")
    else:
        await send_task(message)
        user_last_task_date[user_id] = today

async def send_task(message):
    task = random.choice(expanded_tasks)
    await message.answer(f"*{task['title']}*\n\n{task['description']}", parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "📩 Отправить след")
async def wait_for_response(message: types.Message):
    await message.answer("Жду твой след. Можешь отправить фото, текст или звук.")

@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_trace(message: types.Message):
    await message.answer("Спасибо. След получен. Возвращайся, когда захочешь новое задание 🌿")

    try:
        if message.text:
            content = message.text.strip()
            lower = content.lower()

            if lower in JUNK_WORDS or len(content) <= 2:
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
