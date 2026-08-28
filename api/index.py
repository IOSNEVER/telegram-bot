import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

TOKEN = os.environ.get("BOT_TOKEN")

# State برای ConversationHandler
WAITING_FOR_CODE = 1

# --- توابع هندلر ---
async def start(update: Update, context):
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

async def show_buy_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 پی اس ووچر", callback_data="ps_voucher"),
            InlineKeyboardButton("🔥 هات ووچر", callback_data="hot_voucher")
        ],
        [
            InlineKeyboardButton("💎 یووچر", callback_data="u_voucher"),
            InlineKeyboardButton("💠 سی ووچر", callback_data="c_voucher")
        ],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💳 *خرید ووچر*\n\n"
        "موجودی کیف پول شما : *0 تومان*\n\n"
        "⚠️ شما باید از طریق افزایش موجودی حساب خود را شارژ کنید",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_insufficient_balance(update: Update, context):
    query = update.callback_query
    await query.answer("❌ متاسفانه موجودی حساب شما 0 تومان است", show_alert=True)
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 پی اس ووچر", callback_data="ps_voucher"),
            InlineKeyboardButton("🔥 هات ووچر", callback_data="hot_voucher")
        ],
        [
            InlineKeyboardButton("💎 یووچر", callback_data="u_voucher"),
            InlineKeyboardButton("💠 سی ووچر", callback_data="c_voucher")
        ],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💳 *خرید ووچر*\n\n"
        "موجودی کیف پول شما : *0 تومان*\n\n"
        "⚠️ شما باید از طریق افزایش موجودی حساب خود را شارژ کنید",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def back_to_main(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💳 خرید ووچر", callback_data="buy_voucher")],
        [InlineKeyboardButton("🔄 تبدیل ووچر", callback_data="convert_voucher")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="add_balance")],
        [InlineKeyboardButton("💸 برداشت موجودی", callback_data="withdraw_balance")],
        [InlineKeyboardButton("👥 دعوت دوستان", callback_data="invite_friends")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👋 سلام! خوش اومدی به ربات ما 🤖\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

# --- دکمه دوم: تبدیل ووچر ---
async def convert_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔄 تبدیل یووچر به هات ووچر", callback_data="u_to_hot")],
        [InlineKeyboardButton("🔄 تبدیل یووچر به پی اس ووچر", callback_data="u_to_ps")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 *تبدیل ووچر*\n\nنوع تبدیل مد نظر را انتخاب نمایید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def u_to_hot(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 *تبدیل یووچر به هات ووچر*\n\n"
        "موجودی هات ووچر ربات:\n"
        "248.000 دلار\n\n"
        "تبدیل شما در کمتر از چند دقیقه انجام میشود\n"
        "کد یووچر خود را وارد نمایید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    context.user_data['conversion_type'] = 'u_to_hot'
    return WAITING_FOR_CODE

async def u_to_ps(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 *تبدیل یووچر به پی اس ووچر*\n\n"
        "موجودی پی اس ووچر ربات:\n"
        "187.000 دلار\n\n"
        "تبدیل شما در کمتر از چند دقیقه انجام میشود\n"
        "کد یووچر خود را وارد نمایید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    context.user_data['conversion_type'] = 'u_to_ps'
    return WAITING_FOR_CODE

async def back_to_convert(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔄 تبدیل یووچر به هات ووچر", callback_data="u_to_hot")],
        [InlineKeyboardButton("🔄 تبدیل یووچر به پی اس ووچر", callback_data="u_to_ps")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 *تبدیل ووچر*\n\nنوع تبدیل مد نظر را انتخاب نمایید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def receive_voucher_code(update: Update, context):
    code = update.message.text
    
    await update.message.reply_text(
        "✅ *درخواست بررسی کد ووچر شما انجام شد.*\n\n"
        "پس از بررسی صحت کد یووچر تبدیل شما انجام خواهد شد",
        parse_mode="Markdown"
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("عملیات لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END

# --- ساخت شیء ربات ---
ptb = Application.builder().token(TOKEN).updater(None).build()

# ConversationHandler برای مدیریت فرآیند تبدیل ووچر
conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(u_to_hot, pattern="^u_to_hot$"),
        CallbackQueryHandler(u_to_ps, pattern="^u_to_ps$"),
    ],
    states={
        WAITING_FOR_CODE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_voucher_code)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_convert, pattern="^back_to_convert$"),
        CommandHandler("cancel", cancel),
    ],
)

ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(conv_handler)
ptb.add_handler(CallbackQueryHandler(show_buy_voucher_menu, pattern="^buy_voucher$"))
ptb.add_handler(CallbackQueryHandler(convert_voucher_menu, pattern="^convert_voucher$"))
ptb.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
ptb.add_handler(CallbackQueryHandler(show_insufficient_balance, pattern="^(ps_voucher|hot_voucher|u_voucher|c_voucher)$"))

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
