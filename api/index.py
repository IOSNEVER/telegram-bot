import os
import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler


TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات تستی من 🤖"
    )


application = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)

application.add_handler(CommandHandler("start", start))


async def process_update(data):
    update = Update.de_json(data, application.bot)

    async with application:
        await application.initialize()
        await application.start()
        await application.process_update(update)
        await application.stop()
        await application.shutdown()


def handler(request):
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": "Bot is running!"
        }

    if request.method == "POST":
        import json

        data = json.loads(request.body)

        asyncio.run(process_update(data))

        return {
            "statusCode": 200,
            "body": "OK"
        }

    return {
        "statusCode": 405,
        "body": "Method Not Allowed"
    }
