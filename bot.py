import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات تستی من 🤖"
    )


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN تنظیم نشده!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
