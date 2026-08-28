import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context):
    # ساخت دکمه‌های شیشه‌ای
    keyboard = [
        [InlineKeyboardButton("💳 خرید ووچر", callback_data="buy_voucher")],
        [InlineKeyboardButton("🔄 تبدیل ووچر", callback_data="convert_voucher")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="add_balance")],
        [InlineKeyboardButton("💸 برداشت موجودی", callback_data="withdraw_balance")],
        [InlineKeyboardButton("👥 دعوت دوستان", callback_data="invite_friends")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات ما 🤖\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

# تابع برای پاسخ به کلیک روی دکمه‌ها
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    # بررسی اینکه کاربر روی کدام دکمه کلیک کرده
    if query.data == "buy_voucher":
        await query.edit_message_text("💳 شما گزینه «خرید ووچر» را انتخاب کردید.\n\n(اینجا می‌توانید اطلاعات بیشتر را نمایش دهید)")
    elif query.data == "convert_voucher":
        await query.edit_message_text("🔄 شما گزینه «تبدیل ووچر» را انتخاب کردید.\n\n(اینجا می‌توانید اطلاعات بیشتر را نمایش دهید)")
    elif query.data == "add_balance":
        await query.edit_message_text("💰 شما گزینه «افزایش موجودی» را انتخاب کردید.\n\n(اینجا می‌توانید اطلاعات بیشتر را نمایش دهید)")
    elif query.data == "withdraw_balance":
        await query.edit_message_text("💸 شما گزینه «برداشت موجودی» را انتخاب کردید.\n\n(اینجا می‌توانید اطلاعات بیشتر را نمایش دهید)")
    elif query.data == "invite_friends":
        await query.edit_message_text("👥 شما گزینه «دعوت دوستان» را انتخاب کردید.\n\n(اینجا می‌توانید لینک دعوت را نمایش دهید)")

# ساخت شیء ربات
ptb = Application.builder().token(TOKEN).updater(None).build()
ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CallbackQueryHandler(button_callback))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb.initialize()
    yield
    await ptb.shutdown()

application = FastAPI(lifespan=lifespan)

@application.get("/api")
async def root():
    return {"message": "Telegram bot is running successfully!"}

@application.post("/api")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb.bot)
    await ptb.process_update(update)
    return {"status": "ok"}
