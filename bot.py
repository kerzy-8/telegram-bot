import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# ===== تنظیمات =====
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8276231345  # آیدی عددی خودت

GROUP_ID, USER_ID, COUNT, DELAY = range(4)

# ===== بررسی مالک =====
def is_owner(update: Update):
    return update.effective_user.id == OWNER_ID

# ===== شروع =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return ConversationHandler.END

    await update.message.reply_text("آیدی عددی گروه مقصد رو بفرست:")
    return GROUP_ID

async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group_id"] = int(update.message.text)
    await update.message.reply_text("آیدی عددی فرد رو بفرست:")
    return USER_ID

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["user_id"] = int(update.message.text)
    await update.message.reply_text("چند بار پیام ارسال بشه؟")
    return COUNT

async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["count"] = int(update.message.text)
    await update.message.reply_text("چند ثانیه بین هر پیام فاصله باشه؟")
    return DELAY

async def get_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["delay"] = int(update.message.text)

    await update.message.reply_text("شروع ارسال پیام‌ها...")

    await send_messages(context)

    await update.message.reply_text("✅ ارسال تموم شد.")
    return ConversationHandler.END

# ===== ارسال پیام =====
async def send_messages(context: ContextTypes.DEFAULT_TYPE):
    group_id = context.user_data["group_id"]
    user_id = context.user_data["user_id"]
    count = context.user_data["count"]
    delay = context.user_data["delay"]

    with open("texts.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for i in range(min(count, len(lines))):
        name = lines[i]
        mention = f'<a href="tg://user?id={user_id}">{name}</a>'

        await context.bot.send_message(
            chat_id=group_id,
            text=mention,
            parse_mode="HTML"
        )

        await asyncio.sleep(delay)

# ===== لغو =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END

# ===== اجرای بات =====
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group_id)],
        USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_id)],
        COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_count)],
        DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delay)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv)

print("Bot is running...")
app.run_polling()
