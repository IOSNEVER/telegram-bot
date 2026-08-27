import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("👋 سلام! خوش اومدی به ربات تستی من 🤖")

# ساخت شیء ربات
ptb = Application.builder().token(TOKEN).updater(None).build()
ptb.add_handler(CommandHandler("start", start))

# --- بخش حیاتی برای رفع ارور Vercel ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # راه‌اندازی اولیه ربات قبل از پردازش هر درخواستی
    await ptb.initialize()
    yield
    # خاموش کردن تمیز ربات هنگام بسته شدن (اختیاری اما توصیه شده)
    await ptb.shutdown()

# اتصال lifespan به FastAPI
application = FastAPI(lifespan=lifespan)

@application.get("/api")
async def root():
    return {"message": "Telegram bot is running successfully!"}

@application.post("/api")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb.bot)
    
    # حالا که initialize شده، این خط بدون ارور کار می‌کند
    await ptb.process_update(update)
    
    return {"status": "ok"}
