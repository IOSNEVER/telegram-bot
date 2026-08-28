import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7438564292  # آیدی عددی ادمین

# State برای ConversationHandler
WAITING_FOR_CODE = 1
WAITING_FOR_INCREASE_CODE = 2

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
        "✨ <b>سلام! خوش اومدی به ربات ما</b> ✨\n\n"
        "🤖 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "💳 <b>خرید ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی کیف پول شما:</b> <code>0 تومان</code>\n\n"
        "⚠️ <i>شما باید از طریق افزایش موجودی حساب خود را شارژ کنید</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "💳 <b>خرید ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی کیف پول شما:</b> <code>0 تومان</code>\n\n"
        "⚠️ <i>شما باید از طریق افزایش موجودی حساب خود را شارژ کنید</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "✨ <b>سلام! خوش اومدی به ربات ما</b> ✨\n\n"
        "🤖 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "🔄 <b>تبدیل ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>نوع تبدیل مد نظر را انتخاب نمایید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "🔄 <b>تبدیل یووچر به هات ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی هات ووچر ربات:</b>\n"
        "<code>248.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد یووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "🔄 <b>تبدیل یووچر به پی اس ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی پی اس ووچر ربات:</b>\n"
        "<code>187.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد یووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
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
        "🔄 <b>تبدیل ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>نوع تبدیل مد نظر را انتخاب نمایید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def receive_voucher_code(update: Update, context):
    code = update.message.text
    user = update.message.from_user
    conversion_type = context.user_data.get('conversion_type', 'unknown')
    
    # نمایش پیام تأیید به کاربر
    await update.message.reply_text(
        "✅ <b>درخواست بررسی کد ووچر شما انجام شد.</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⏳ <i>پس از بررسی صحت کد یووچر تبدیل شما انجام خواهد شد</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )
    
    # ارسال اطلاعات به ادمین
    conversion_text = {
        'u_to_hot': 'یووچر ➡️ هات ووچر',
        'u_to_ps': 'یووچر ➡️ پی اس ووچر'
    }.get(conversion_type, 'نامشخص')
    
    admin_message = (
        "🔔 <b>درخواست تبدیل ووچر جدید</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>کاربر:</b> {user.full_name}\n"
        f"🆔 <b>آیدی عددی:</b> <code>{user.id}</code>\n"
        f"🔄 <b>نوع تبدیل:</b> {conversion_text}\n"
        f"🔑 <b>کد ووچر:</b>\n<code>{code}</code>\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending message to admin: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

# --- دکمه سوم: افزایش موجودی ---
async def add_balance_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("💎 یوووچر", callback_data="increase_u_voucher"),
            InlineKeyboardButton("🎮 پی اس ووچر", callback_data="increase_ps_voucher")
        ],
        [
            InlineKeyboardButton("🔥 هات ووچر", callback_data="increase_hot_voucher"),
            InlineKeyboardButton("💠 سی ووچر", callback_data="increase_c_voucher")
        ],
        [
            InlineKeyboardButton("💎 تون", callback_data="increase_ton"),
            InlineKeyboardButton("🔺 ترون", callback_data="increase_tron"),
            InlineKeyboardButton("💵 تتر", callback_data="increase_tether")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💰 <b>افزایش موجودی</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>روش افزایش موجودی را انتخاب کنید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def increase_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    voucher_type = query.data.replace('increase_', '')
    voucher_names = {
        'u_voucher': 'یوووچر',
        'ps_voucher': 'پی اس ووچر',
        'hot_voucher': 'هات ووچر',
        'c_voucher': 'سی ووچر'
    }
    voucher_name = voucher_names.get(voucher_type, 'نامشخص')
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_add_balance")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 <b>افزایش موجودی با {voucher_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💵 <i>افزایش موجودی شما به نرخ دلار روز انجام میشود</i>\n\n"
        f"🔑 <b>کد {voucher_name} خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    context.user_data['increase_type'] = voucher_type
    return WAITING_FOR_INCREASE_CODE

async def increase_crypto_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    crypto_type = query.data.replace('increase_', '')
    crypto_names = {
        'ton': 'تون',
        'tron': 'ترون',
        'tether': 'تتر'
    }
    crypto_name = crypto_names.get(crypto_type, 'نامشخص')
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_add_balance")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 <b>افزایش موجودی با {crypto_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📞 <i>برای افزایش موجودی از طریق {crypto_name} به پشتیبانی پیام بدهید</i>\n\n"
        "🆔 <b>آیدی پشتیبانی:</b>\n"
        "<code>آیدی پشتیبانی اینجا قرار می‌گیرد</code>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def back_to_add_balance(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("💎 یوووچر", callback_data="increase_u_voucher"),
            InlineKeyboardButton("🎮 پی اس ووچر", callback_data="increase_ps_voucher")
        ],
        [
            InlineKeyboardButton("🔥 هات ووچر", callback_data="increase_hot_voucher"),
            InlineKeyboardButton("💠 سی ووچر", callback_data="increase_c_voucher")
        ],
        [
            InlineKeyboardButton("💎 تون", callback_data="increase_ton"),
            InlineKeyboardButton("🔺 ترون", callback_data="increase_tron"),
            InlineKeyboardButton("💵 تتر", callback_data="increase_tether")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💰 <b>افزایش موجودی</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>روش افزایش موجودی را انتخاب کنید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def receive_increase_code(update: Update, context):
    code = update.message.text
    user = update.message.from_user
    increase_type = context.user_data.get('increase_type', 'unknown')
    
    voucher_names = {
        'u_voucher': 'یوووچر',
        'ps_voucher': 'پی اس ووچر',
        'hot_voucher': 'هات ووچر',
        'c_voucher': 'سی ووچر'
    }
    voucher_name = voucher_names.get(increase_type, 'نامشخص')
    
    # نمایش پیام تأیید به کاربر
    await update.message.reply_text(
        "✅ <b>درخواست افزایش موجودی شما ثبت شد.</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⏳ <i>پس از بررسی صحت کد، مبلغ به کیف پول شما واریز میشود</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )
    
    # ارسال اطلاعات به ادمین
    admin_message = (
        "🔔 <b>درخواست افزایش موجودی جدید</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>کاربر:</b> {user.full_name}\n"
        f"🆔 <b>آیدی عددی:</b> <code>{user.id}</code>\n"
        f"💎 <b>نوع ووچر:</b> {voucher_name}\n"
        f"🔑 <b>کد ووچر:</b>\n<code>{code}</code>\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending message to admin: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("❌ عملیات لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END

# --- ساخت شیء ربات ---
ptb = Application.builder().token(TOKEN).updater(None).build()

# ConversationHandler برای تبدیل ووچر
conv_handler_convert = ConversationHandler(
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

# ConversationHandler برای افزایش موجودی
conv_handler_increase = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(increase_voucher_menu, pattern="^increase_(u_voucher|ps_voucher|hot_voucher|c_voucher)$"),
        CallbackQueryHandler(increase_crypto_menu, pattern="^increase_(ton|tron|tether)$"),
    ],
    states={
        WAITING_FOR_INCREASE_CODE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_increase_code)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_add_balance, pattern="^back_to_add_balance$"),
        CommandHandler("cancel", cancel),
    ],
)

ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(conv_handler_convert)
ptb.add_handler(conv_handler_increase)
ptb.add_handler(CallbackQueryHandler(show_buy_voucher_menu, pattern="^buy_voucher$"))
ptb.add_handler(CallbackQueryHandler(convert_voucher_menu, pattern="^convert_voucher$"))
ptb.add_handler(CallbackQueryHandler(add_balance_menu, pattern="^add_balance$"))
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
