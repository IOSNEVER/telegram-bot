import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler

# دریافت توکن از متغیرهای محیطی Vercel
TOKEN = os.environ.get("BOT_TOKEN")

# --- تعریف دستورات ربات ---
async def start(update: Update, context):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات تستی من 🤖"
    )

# ساخت شیء ربات تلگرام (تغییر نام به ptb برای جلوگیری از تداخل)
ptb = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)
ptb.add_handler(CommandHandler("start", start))

# --- ساخت سرور وب برای Vercel ---
# Vercel دقیقاً به دنبال متغیری به نام application می گردد که یک سرور وب باشد
application = FastAPI()

@application.get("/")
async def root():
    return {"message": "Telegram bot is running successfully!"}

@application.post("/")
async def webhook(request: Request):
    # دریافت دیتای ارسالی از سمت تلگرام
    data = await request.json()
    
    # تبدیل دیتا به آبجکت Update تلگرام
    update = Update.de_json(data, ptb.bot)
    
    # پردازش آپدیت توسط ربات (چون FastAPI async است، نیازی به asyncio.run نیست)
    await ptb.process_update(update)
    
    return {"status": "ok"}
