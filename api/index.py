import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
from supabase import create_client, Client

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7438564292

# تنظیمات Supabase
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

WAITING_FOR_CODE = 1
WAITING_FOR_INCREASE_CODE = 2

REFERRAL_REWARD = 200
REFERRAL_REQUIRED = 5

# --- توابع کمکی Supabase ---
def get_user_data(user_id):
    if not supabase:
        return None
    try:
        result = supabase.table("referrals").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user data: {e}")
        return None

def create_user(user_id, referred_by=None):
    if not supabase:
        return
    try:
        supabase.table("referrals").insert({
            "user_id": user_id,
            "referred_by": referred_by,
            "invited_list": [],
            "is_rewarded": False
        }).execute()
    except Exception as e:
        print(f"Error creating user: {e}")

def add_invited_user(referrer_id, invited_id):
    if not supabase:
        return
    try:
        user_data = get_user_data(referrer_id)
        if not user_data:
            create_user(referrer_id)
            user_data = get_user_data(referrer_id)
        
        invited_list = user_data.get("invited_list", [])
        if invited_id not in invited_list:
            invited_list.append(invited_id)
            supabase.table("referrals").update({
                "invited_list": invited_list
            }).eq("user_id", referrer_id).execute()
    except Exception as e:
        print(f"Error adding invited user: {e}")

def mark_user_rewarded(user_id):
    if not supabase:
        return
    try:
        supabase.table("referrals").update({
            "is_rewarded": True
        }).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Error marking user rewarded: {e}")

# --- هندلرها ---
async def start(update: Update, context):
    user = update.effective_user
    user_name = user.first_name
    
    if context.args and len(context.args) > 0:
        if context.args[0].startswith("ref_"):
            referrer_id = int(context.args[0].replace("ref_", ""))
            
            if user.id != referrer_id:
                user_data = get_user_data(user.id)
                if not user_data:
                    create_user(user.id, referrer_id)
                    add_invited_user(referrer_id, user.id)
                    
                    try:
                        await context.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=(
                                "🎉 <b>دعوت جدید!</b>\n\n"
                                "━━━━━━━━━━━━━━━━━━\n"
                                f"👤 <b>دعوت کننده:</b> <code>{referrer_id}</code>\n"
                                f"🆕 <b>کاربر جدید:</b> {user.full_name}\n"
                                f"🆔 <b>آیدی:</b> <code>{user.id}</code>\n"
                                "━━━━━━━━━━━━━━━━━━"
                            ),
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        print(f"Error: {e}")
                    
                    referrer_data = get_user_data(referrer_id)
                    if referrer_data:
                        invited_count = len(referrer_data.get("invited_list", []))
                        is_rewarded = referrer_data.get("is_rewarded", False)
                        
                        if invited_count >= REFERRAL_REQUIRED and not is_rewarded:
                            mark_user_rewarded(referrer_id)
                            
                            try:
                                await context.bot.send_message(
                                    chat_id=referrer_id,
                                    text=(
                                        "🎊 <b>تبریک! شما برنده شدید!</b> 🎊\n\n"
                                        "━━━━━━━━━━━━━━━━━━\n"
                                        f"✅ شما {REFERRAL_REQUIRED} دوست دعوت کردید!\n"
                                        f"💰 <b>{REFERRAL_REWARD} تومان هات ووچر</b> به حساب شما واریز شد!\n"
                                        "━━━━━━━━━━━━━━━━━━"
                                    ),
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                print(f"Error sending reward: {e}")
                            
                            try:
                                await context.bot.send_message(
                                    chat_id=ADMIN_ID,
                                    text=(
                                        "💰 <b>پاداش واریز شد!</b>\n\n"
                                        "━━━━━━━━━━━━━━━━━━\n"
                                        f"👤 <b>کاربر:</b> <code>{referrer_id}</code>\n"
                                        f"💎 <b>مبلغ:</b> {REFERRAL_REWARD} تومان هات ووچر\n"
                                        "━━━━━━━━━━━━━━━━━━"
                                    ),
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                print(f"Error: {e}")
    else:
        user_data = get_user_data(user.id)
        if not user_data:
            create_user(user.id)
    
    keyboard = [
        [InlineKeyboardButton("💳 خرید ووچر", callback_data="buy_voucher")],
        [InlineKeyboardButton("🔄 تبدیل ووچر", callback_data="convert_voucher")],
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="add_balance")],
        [InlineKeyboardButton("💸 برداشت موجودی", callback_data="withdraw_balance")],
        [InlineKeyboardButton("👥 دعوت دوستان", callback_data="invite_friends")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سلام خوش اومدی <b>{user_name}</b> عزیز ❤️\n"
        "روی دکمه مورد نظر خود کلیک کنید 👇\n\n"
        "به تبلیغات تلگرام در ربات ما توجه نکنید ⛔",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def show_buy_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎮 پی اس ووچر", callback_data="ps_voucher"), InlineKeyboardButton("🔥 هات ووچر", callback_data="hot_voucher")],
        [InlineKeyboardButton("💎 یووچر", callback_data="u_voucher"), InlineKeyboardButton("💠 سی ووچر", callback_data="c_voucher")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "💳 <b>خرید ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی کیف پول شما:</b> <code>0 تومان</code>\n\n"
        "⚠️ <i>شما باید از طریق افزایش موجودی حساب خود را شارژ کنید</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_insufficient_balance(update: Update, context):
    query = update.callback_query
    await query.answer("❌ متاسفانه موجودی حساب شما 0 تومان است", show_alert=True)
    
    keyboard = [
        [InlineKeyboardButton("🎮 پی اس ووچر", callback_data="ps_voucher"), InlineKeyboardButton("🔥 هات ووچر", callback_data="hot_voucher")],
        [InlineKeyboardButton("💎 یووچر", callback_data="u_voucher"), InlineKeyboardButton("💠 سی ووچر", callback_data="c_voucher")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "💳 <b>خرید ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی کیف پول شما:</b> <code>0 تومان</code>\n\n"
        "⚠️ <i>شما باید از طریق افزایش موجودی حساب خود را شارژ کنید</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
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
    
    await query.edit_message_text(
        f"سلام خوش اومدی <b>{update.effective_user.first_name}</b> عزیز ❤️\n"
        "روی دکمه مورد نظر خود کلیک کنید 👇\n\n"
        "به تبلیغات تلگرام در ربات ما توجه نکنید ⛔",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def convert_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔄 تبدیل یووچر به هات ووچر", callback_data="u_to_hot")],
        [InlineKeyboardButton("🔄 تبدیل یووچر به پی اس ووچر", callback_data="u_to_ps")],
        [InlineKeyboardButton("🔥 تبدیل هات ووچر به پرمیوم ووچر", callback_data="hot_to_premium")],
        [InlineKeyboardButton("💎 تبدیل پرمیوم ووچر به هات ووچر", callback_data="premium_to_hot")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>نوع تبدیل مد نظر را انتخاب نمایید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def u_to_hot(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل یووچر به هات ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی هات ووچر ربات:</b>\n<code>248.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد یووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data['conversion_type'] = 'u_to_hot'
    return WAITING_FOR_CODE

async def u_to_ps(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل یووچر به پی اس ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی پی اس ووچر ربات:</b>\n<code>187.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد یووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data['conversion_type'] = 'u_to_ps'
    return WAITING_FOR_CODE

async def hot_to_premium(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل هات ووچر به پرمیوم ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی پرمیوم ووچر ربات:</b>\n<code>150.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد هات ووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data['conversion_type'] = 'hot_to_premium'
    return WAITING_FOR_CODE

async def premium_to_hot(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_convert")]]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل پرمیوم ووچر به هات ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>موجودی هات ووچر ربات:</b>\n<code>248.000 دلار</code>\n\n"
        "⚡ <i>تبدیل شما در کمتر از چند دقیقه انجام میشود</i>\n\n"
        "🔑 <b>کد پرمیوم ووچر خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data['conversion_type'] = 'premium_to_hot'
    return WAITING_FOR_CODE

async def back_to_convert(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔄 تبدیل یووچر به هات ووچر", callback_data="u_to_hot")],
        [InlineKeyboardButton("🔄 تبدیل یووچر به پی اس ووچر", callback_data="u_to_ps")],
        [InlineKeyboardButton("🔥 تبدیل هات ووچر به پرمیوم ووچر", callback_data="hot_to_premium")],
        [InlineKeyboardButton("💎 تبدیل پرمیوم ووچر به هات ووچر", callback_data="premium_to_hot")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "🔄 <b>تبدیل ووچر</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>نوع تبدیل مد نظر را انتخاب نمایید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def receive_voucher_code(update: Update, context):
    code = update.message.text
    user = update.message.from_user
    conversion_type = context.user_data.get('conversion_type', 'unknown')
    
    await update.message.reply_text(
        "✅ <b>درخواست بررسی کد ووچر شما انجام شد.</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⏳ <i>پس از بررسی صحت کد یووچر تبدیل شما انجام خواهد شد</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )
    
    conversion_text = {
        'u_to_hot': 'یووچر ➡️ هات ووچر',
        'u_to_ps': 'یووچر ➡️ پی اس ووچر',
        'hot_to_premium': 'هات ووچر ➡️ پرمیوم ووچر',
        'premium_to_hot': 'پرمیوم ووچر ➡️ هات ووچر'
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
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="HTML")
    except Exception as e:
        print(f"Error: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def add_balance_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💎 یوووچر", callback_data="increase_u_voucher"), InlineKeyboardButton("🎮 پی اس ووچر", callback_data="increase_ps_voucher")],
        [InlineKeyboardButton("🔥 هات ووچر", callback_data="increase_hot_voucher"), InlineKeyboardButton("💠 سی ووچر", callback_data="increase_c_voucher")],
        [InlineKeyboardButton("💎 تون", callback_data="increase_ton"), InlineKeyboardButton("🔺 ترون", callback_data="increase_tron"), InlineKeyboardButton("💵 تتر", callback_data="increase_tether")],
        [InlineKeyboardButton("💳 ریالی", callback_data="increase_rial")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "💰 <b>افزایش موجودی</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📋 <i>روش افزایش موجودی را انتخاب کنید:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def increase_voucher_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    voucher_type = query.data.replace('increase_', '')
    voucher_names = {'u_voucher': 'یوووچر', 'ps_voucher': 'پی اس ووچر', 'hot_voucher': 'هات ووچر', 'c_voucher': 'سی ووچر'}
    voucher_name = voucher_names.get(voucher_type, 'نامشخص')
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_add_balance")]]
    
    await query.edit_message_text(
        f"💰 <b>افزایش موجودی با {voucher_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💵 <i>افزایش موجودی شما به نرخ دلار روز انجام میشود</i>\n\n"
        f"🔑 <b>کد {voucher_name} خود را وارد نمایید:</b>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data['increase_type'] = voucher_type
    return WAITING_FOR_INCREASE_CODE

async def increase_crypto_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    crypto_type = query.data.replace('increase_', '')
    crypto_names = {'ton': 'تون', 'tron': 'ترون', 'tether': 'تتر'}
    crypto_name = crypto_names.get(crypto_type, 'نامشخص')
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_add_balance")]]
    
    await query.edit_message_text(
        f"💰 <b>افزایش موجودی با {crypto_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📞 <i>برای افزایش موجودی از طریق {crypto_name} به پشتیبانی پیام بدهید</i>\n\n"
        "🆔 <b>آیدی پشتیبانی:</b>\n<code>@supp_win</code>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def increase_rial_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_add_balance")]]
    
    await query.edit_message_text(
        "💳 <b>افزایش موجودی ریالی</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📞 <i>برای افزایش موجودی از طریق ریالی به پشتیبانی پیام بدهید</i>\n\n"
        "🆔 <b>آیدی پشتیبانی:</b>\n<code>@supp_win</code>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def back_to_add_balance(update: Update, context):
    query = update.callback_query
    await query.answer()
