import json
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROUP_ID = -1003812696742
SCHEDULE_THREAD_ID = 773
USERS_FILE = "users.json"
SCHEDULE_FILE = "schedule.json"


# Простой веб-сервер чтобы Replit не засыпал
class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Harmony Life Bot is running!")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), KeepAlive)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []


def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)


def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    return None


def save_schedule(chat_id, message_id):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "message_id": message_id}, f)


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📅 Расписание"), KeyboardButton("📞 Связаться")]],
        resize_keyboard=True
    )


def get_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ О нас", url="http://t.me/harmony_life_ry_bot/site"),
            InlineKeyboardButton("📜 Устав", url="http://t.me/harmony_life_ry_bot/ustav")
        ],
        [
            InlineKeyboardButton("🏢 Центр развития и услуг", url="http://t.me/harmony_life_ry_bot/center")
        ],
        [
            InlineKeyboardButton("📍 Гид жителя Kainuu", url="http://t.me/harmony_life_ry_bot/GIDOFKAINUU")
        ],
        [
            InlineKeyboardButton("🏠 Гид новосёла Финляндии", url="http://t.me/harmony_life_ry_bot/Tervetuloa")
        ],
        [
            InlineKeyboardButton("🎮 Игры", url="http://t.me/harmony_life_ry_bot/Game")
        ],
        [
            InlineKeyboardButton("📘 Facebook", url="https://www.facebook.com/share/1AuAbU1Z2G"),
            InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/harmony.life_ry")
        ],
        [
            InlineKeyboardButton("👤 Написать председателю", url="https://t.me/Harmony_Ry")
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    with open("logo.jpg", "rb") as photo:
        msg = await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption="👋 Добро пожаловать в Harmony Life ry!\n\nМы — общественная организация в Каяани 🌿\n\nВыберите нужный раздел:",
            reply_markup=get_inline_keyboard()
        )

    try:
        await context.bot.pin_chat_message(chat_id=user_id, message_id=msg.message_id)
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=user_id,
        text="Используйте кнопки ниже 👇",
        reply_markup=get_main_keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📅 Расписание":
        schedule = load_schedule()
        if schedule:
            try:
                await context.bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=schedule["chat_id"],
                    message_id=schedule["message_id"]
                )
            except Exception:
                await update.message.reply_text("Не удалось загрузить расписание. Попробуйте позже.")
        else:
            await update.message.reply_text("Расписание пока не опубликовано. Следите за обновлениями! 🌿")

    elif text == "📞 Связаться":
        await update.message.reply_text(
            "Напишите напрямую председателю Harmony Life ry:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Написать председателю", url="https://t.me/Harmony_Ry")]
            ])
        )


async def monitor_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if (message.chat_id == GROUP_ID and
            getattr(message, 'message_thread_id', None) == SCHEDULE_THREAD_ID):

        save_schedule(message.chat_id, message.message_id)

        users = load_users()
        for uid in users:
            try:
                await context.bot.forward_message(
                    chat_id=uid,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )
            except Exception as e:
                logging.error(f"Не удалось переслать пользователю {uid}: {e}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
app.add_handler(MessageHandler(filters.Chat(GROUP_ID), monitor_group))
app.run_polling()
