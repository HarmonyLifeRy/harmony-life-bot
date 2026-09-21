import json
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ChatMemberHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROUP_ID = -1003812696742
GROUP_LINK = "https://t.me/Harmony_Life_Ry"
SCHEDULE_THREAD_ID = 773
USERS_FILE = "users.json"
SCHEDULE_FILE = "schedule.json"


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
        [[KeyboardButton("💜 Группа"), KeyboardButton("📅 Расписание"), KeyboardButton("📞 Связаться")]],
        resize_keyboard=True
    )

def get_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💜 Перейти в группу Harmony Life", url=GROUP_LINK)],
        [
            InlineKeyboardButton("🌸 О нас", url="http://t.me/harmony_life_ry_bot/site"),
            InlineKeyboardButton("📜 Устав", url="http://t.me/harmony_life_ry_bot/ustav")
        ],
        [InlineKeyboardButton("✨ Центр развития и услуг", url="http://t.me/harmony_life_ry_bot/center")],
        [InlineKeyboardButton("📍 Гид жителя Kainuu", url="http://t.me/harmony_life_ry_bot/GIDOFKAINUU")],
        [InlineKeyboardButton("🏠 Гид новосёла Финляндии", url="http://t.me/harmony_life_ry_bot/Tervetuloa")],
        [InlineKeyboardButton("🎮 Игры", url="http://t.me/harmony_life_ry_bot/Game")],
        [
            InlineKeyboardButton("Facebook", url="https://www.facebook.com/share/1AuAbU1Z2G"),
            InlineKeyboardButton("Instagram", url="https://www.instagram.com/harmony.life_ry")
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    with open("logo.jpg", "rb") as photo:
        msg = await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=(
                "🌸 Здравствуйте! Я — Робот-помощник Harmony Life ry 🤖\n\n"
                "Я здесь как навигатор — помогу найти нужное и направлю туда, где происходит всё важное ✨\n\n"
                "💜 Harmony Life ry — общественная организация в Финляндии, объединяющая людей разных культур "
                "для интеграции, саморазвития и творчества 🌿\n\n"
                "👇 Всё общение, события и новости — в нашей группе:"
            ),
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
                await update.message.reply_text("Расписание пока не опубликовано. Следите за обновлениями! 🌿")
        else:
            await update.message.reply_text("Расписание пока не опубликовано. Следите за обновлениями! 🌿")

    elif text == "💜 Группа":
        await update.message.reply_text(
            "💜 Наша группа в Telegram 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💜 Перейти в группу Harmony Life", url=GROUP_LINK)]
            ])
        )

    elif text == "📞 Связаться":
        await update.message.reply_text(
            "💜 Наша группа в Telegram 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💜 Перейти в группу Harmony Life", url=GROUP_LINK)]
            ])
        )

    else:
        await update.message.reply_text(
            "🌸 Извините, я пока не умею отвечать — я навигатор!\n\n"
            "Зато в нашей группе вам обязательно помогут 💜",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💜 Перейти в группу Harmony Life", url=GROUP_LINK)]
            ])
        )


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.new_chat_member.status == "member" and result.old_chat_member.status in ["left", "kicked"]:
        user_id = result.new_chat_member.user.id
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🌸 Здравствуйте!\n\n"
                    "Спасибо за ваш интерес к Harmony Life ry 💜\n\n"
                    "Ваша заявка принята. В ближайшее время с вами свяжется "
                    "представитель нашей организации."
                )
            )
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение новому участнику {user_id}: {e}")


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
                await context.bot.send_message(
                    chat_id=uid,
                    text="💜 Данное мероприятие доступно для членов сообщества Harmony Life ry."
                )
            except Exception as e:
                logging.error(f"Не удалось переслать пользователю {uid}: {e}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
app.add_handler(MessageHandler(filters.Chat(GROUP_ID), monitor_group))
app.run_polling(allowed_updates=["message", "chat_member"])
