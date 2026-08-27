import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("👋 سلام! خوش اومدی به ربات تستی من 🤖")

ptb = Application.builder().token(TOKEN).updater(None).build()
ptb.add_handler(CommandHandler("start", start))

# Vercel به دنبال متغیری به نام application می‌گردد
application = FastAPI()

# گوش دادن به مسیر ریشه (/)
@application.get("/")
async def root():
    return {"message": "Telegram bot is running successfully!"}

@application.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb.bot)
    await ptb.process_update(update)
    return {"status": "ok"}
