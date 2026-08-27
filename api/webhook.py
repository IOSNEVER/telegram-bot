import os

from telegram import Update
from telegram.ext import Application, CommandHandler


TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات تستی من 🤖"
    )


application = Application.builder().token(TOKEN).build()

application.add_handler(
    CommandHandler("start", start)
)


async def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 200,
            "body": "Telegram bot is running!"
        }

    body = await request.json()

    update = Update.de_json(
        body,
        application.bot
    )

    await application.process_update(update)

    return {
        "statusCode": 200,
        "body": "OK"
    }
