#!/usr/bin/env python3
# arash_bot_super.py
# Requires: pip install pyTelegramBotAPI
# UTF-8 encoded

import telebot
from telebot import types
import json
import os
import random
import traceback
from datetime import datetime, timedelta

# ================= CONFIG =================
TOKEN_BOT = os.getenv("TOKEN_BOT") or "Token Bot"
ADMIN_IDS = [6847589554]             # replace with your admin ids
SUPPORT_ID = 7108658689              # support forward id
CREATOR_ID = 6847589554              # visible on 'creator' button
DATA_DIR = "bot_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
RECEIPTS_FILE = os.path.join(DATA_DIR, "receipts.json")
BROADCAST_LOG = os.path.join(DATA_DIR, "broadcast.json")

PRICE_PER_STAR = 1500
CODE_EXPIRY_MINUTES = 3

# ensure support in admins
if SUPPORT_ID not in ADMIN_IDS:
    ADMIN_IDS.append(SUPPORT_ID)

# create data dir
os.makedirs(DATA_DIR, exist_ok=True)

# ================= persistence helpers =================
def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# load databases
users_db = load_json(USERS_FILE) or {}
orders_db = load_json(ORDERS_FILE) or []
receipts_db = load_json(RECEIPTS_FILE) or []
broadcast_db = load_json(BROADCAST_LOG) or []

# ================ config data ================
COUNTRIES = {
    "🇺🇸 USA": 40000,
    "🇨🇦 Canada": 40000,
    "🇮🇷 Iran": 150000,
    "🇸🇦 Saudi Arabia": 100000,
}

# multilingual messages
MESSAGES = {
    "fa": {
        "welcome": "👋 سلام! خوش آمدی به ربات.",
        "menu": "منوی اصلی:",
        "choose_country": "🌍 کشور شماره مجازی را انتخاب کن:",
        "price_for": "💵 قیمت برای {country}: {price:,} تومان",
        "confirm_order": "آیا می‌خواهی سفارش را اضافه کنی به سبد؟",
        "enter_qty": "🔢 تعداد را وارد کن (عدد صحیح):",
        "cart_added": "🧾 آیتم به سبد اضافه شد.",
        "cart_empty": "🛒 سبد شما خالی است.",
        "view_cart": "🧾 سبد خرید شما:\n{summary}\n\n💰 مجموع: {total:,} تومان",
        "checkout_confirm": "آیا می‌خواهی سفارش را نهایی کنی؟",
        "enter_name": "✍️ لطفاً نام و نام خانوادگی را وارد کن:",
        "send_contact": "📲 شماره خود را با دکمه زیر ارسال کن:",
        "enter_code": "⏰ کد ارسال شد. لطفاً وارد کن:",
        "invalid_code": "❌ کد اشتباه یا منقضی شده.",
        "order_registered": "🎉 سفارش ثبت شد! کد: {order_id}",
        "profile_created": "✅ پروفایل بروزرسانی شد.",
        "wallet_balance": "💰 موجودی: {amount:,} تومان",
        "send_receipt": "📸 لطفاً عکس فیش پرداخت را ارسال کن.",
        "receipt_sent_admin": "📤 رسید ارسال شد؛ پس از تایید، کیف‌پول شارژ می‌شود.",
        "receipt_approved": "✅ رسید تایید شد؛ کیف‌پول شما {amount:,} تومان شارژ شد.",
        "receipt_rejected": "❌ رسید رد شد.",
        "support_prompt": "🛠 لطفاً پیام پشتیبانی خود را ارسال کن:",
        "support_sent": "پیام شما برای پشتیبانی ارسال شد."
    },
    "en": {
        "welcome": "👋 Welcome to the bot!",
        "menu": "Main menu:",
        "choose_country": "🌍 Choose virtual-number country:",
        "price_for": "💵 Price for {country}: {price:,} Toman",
        "confirm_order": "Do you want to add this to your cart?",
        "enter_qty": "🔢 Enter quantity (integer):",
        "cart_added": "🧾 Item added to cart.",
        "cart_empty": "🛒 Your cart is empty.",
        "view_cart": "🧾 Your cart:\n{summary}\n\n💰 Total: {total:,} Toman",
        "checkout_confirm": "Do you want to complete the checkout?",
        "enter_name": "✍️ Please enter your full name:",
        "send_contact": "📲 Please send your Telegram contact (button):",
        "enter_code": "⏰ Code sent. Please enter it:",
        "invalid_code": "❌ Code invalid or expired.",
        "order_registered": "🎉 Order registered! ID: {order_id}",
        "profile_created": "✅ Profile updated.",
        "wallet_balance": "💰 Balance: {amount:,} Toman",
        "send_receipt": "📸 Please send payment receipt photo.",
        "receipt_sent_admin": "📤 Receipt sent for review.",
        "receipt_approved": "✅ Receipt approved; wallet credited {amount:,} Toman.",
        "receipt_rejected": "❌ Receipt rejected.",
        "support_prompt": "🛠 Please send your support message:",
        "support_sent": "Your support message was sent."
    },
    "ar": {
        "welcome": "👋 مرحباً بك في البوت!",
        "menu": "القائمة الرئيسية:",
        "choose_country": "🌍 اختر دولة الرقم الافتراضي:",
        "price_for": "💵 السعر لـ {country}: {price:,} تومان",
        "confirm_order": "هل تريد إضافة هذا للسلة؟",
        "enter_qty": "🔢 أدخل الكمية (عدد صحيح):",
        "cart_added": "🧾 تم إضافة العنصر للسلة.",
        "cart_empty": "🛒 سلتك فارغة.",
        "view_cart": "🧾 سلتك:\n{summary}\n\n💰 المجموع: {total:,} تومان",
        "checkout_confirm": "هل تريد إنهاء الطلب؟",
        "enter_name": "✍️ الرجاء إدخال اسمك الكامل:",
        "send_contact": "📲 الرجاء إرسال جهة اتصال تلغرام (زر):",
        "enter_code": "⏰ تم إرسال الرمز. الرجاء إدخاله:",
        "invalid_code": "❌ الرمز غير صالح أو منتهي.",
        "order_registered": "🎉 تم تسجيل الطلب! رقم: {order_id}",
        "profile_created": "✅ تم تحديث الملف الشخصي.",
        "wallet_balance": "💰 الرصيد: {amount:,} تومان",
        "send_receipt": "📸 الرجاء إرسال إيصال الدفع صورة.",
        "receipt_sent_admin": "📤 تم إرسال الإيصال للمراجعة.",
        "receipt_approved": "✅ تم الموافقة؛ تم شحن المحفظة بمقدار {amount:,} تومان.",
        "receipt_rejected": "❌ تم رفض الإيصال.",
        "support_prompt": "🛠 أرسل رسالة الدعم:",
        "support_sent": "تم إرسال رسالتك للدعم."
    }
}

# ================ Utilities ================
def user_profile(chat_id):
    key = str(chat_id)
    if key not in users_db:
        users_db[key] = {
            "first_name": "",
            "last_name": "",
            "phone": "",
            "lang": "fa",
            "wallet": 0,
            "points": 0,
            "vip": False,
            "created_at": datetime.utcnow().isoformat()
        }
        save_json(USERS_FILE, users_db)
    return users_db[key]

def set_profile(chat_id, profile):
    users_db[str(chat_id)] = profile
    save_json(USERS_FILE, users_db)

def get_msg(chat_id, key, **kw):
    prof = user_profile(chat_id)
    lang = prof.get("lang", "fa")
    template = MESSAGES.get(lang, MESSAGES["fa"]).get(key, "")
    return template.format(**kw) if kw else template

def gen_code():
    return "{:06d}".format(random.randint(0, 999999))

def gen_order_id(prefix="ARSH"):
    now = datetime.utcnow().strftime("%y%m%d%H%M%S")
    return f"{prefix}-{now}-{random.randint(1000,9999)}"

def save_order(order):
    orders_db.append(order)
    save_json(ORDERS_FILE, orders_db)

def save_receipt(r):
    receipts_db.append(r)
    save_json(RECEIPTS_FILE, receipts_db)

def user_cart_summary(cart):
    lines = []
    total = 0
    for idx, item in enumerate(cart, 1):
        if item["kind"] == "number":
            lines.append(f"{idx}. {item['country']} × {item['qty']} — {item['price']:,} each")
            total += item['price'] * item['qty']
        elif item["kind"] == "stars":
            lines.append(f"{idx}. ⭐ {item['qty']} × {item['price']:,}")
            total += item['price'] * item['qty']
    return "\n".join(lines), total

# ================ Bot init ================
bot = telebot.TeleBot(TOKEN_BOT)
user_states = {}  # chat_id -> state dict (flow, stage, temp data)

# ================ Markups/UI ================
def main_menu_markup(chat_id):
    prof = user_profile(chat_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(types.KeyboardButton("📱 خرید شماره مجازی"), types.KeyboardButton("⭐ خرید استارز"))
    kb.add(types.KeyboardButton("🧾 سبد خرید"), types.KeyboardButton("💳 کیف‌پول / شارژ"))
    kb.add(types.KeyboardButton("👤 پروفایل"), types.KeyboardButton("ℹ️ درباره ما"))
    kb.add(types.KeyboardButton("🛠 پشتیبانی"), types.KeyboardButton("🌐 تغییر زبان"))
    kb.add(types.KeyboardButton("👨‍💻 سازنده"), types.KeyboardButton("📣 خبر/اعلان"))
    return kb

def country_choice_markup(chat_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for c, p in COUNTRIES.items():
        kb.add(types.KeyboardButton(f"{c} — {p:,}"))
    kb.add(types.KeyboardButton("🔙 بازگشت"))
    return kb

def qty_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("1"), types.KeyboardButton("2"), types.KeyboardButton("3"))
    kb.add(types.KeyboardButton("🔙 بازگشت"))
    return kb

def confirm_yesno_markup(chat_id):
    prof = user_profile(chat_id)
    lang = prof.get("lang", "fa")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # localized labels:
    yes = {"fa":"✅ تایید سفارش","en":"✅ Confirm Order","ar":"✅ تأكيد"}[lang if lang in ["fa","en","ar"] else "fa"]
    no = {"fa":"❌ لغو","en":"❌ Cancel","ar":"❌ إلغاء"}[lang if lang in ["fa","en","ar"] else "fa"]
    kb.add(types.KeyboardButton(yes), types.KeyboardButton(no))
    return kb

def contact_request_kb(lang="fa"):
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    labels = {"fa":"📲 ارسال شماره من","en":"📲 Send my contact","ar":"📲 إرسال رقمي"}
    kb.add(types.KeyboardButton(labels.get(lang,"📲 ارسال شماره من"), request_contact=True))
    kb.add(types.KeyboardButton({"fa":"❌ انصراف","en":"❌ Cancel","ar":"❌ إلغاء"}.get(lang)))
    return kb

# ================ Handlers ================
@bot.message_handler(commands=["start","help"])
def cmd_start(m):
    chat_id = m.chat.id
    prof = user_profile(chat_id)
    bot.send_message(chat_id, get_msg(chat_id,"welcome"))
    bot.send_message(chat_id, get_msg(chat_id,"menu"), reply_markup=main_menu_markup(chat_id))

@bot.message_handler(func=lambda m: m.text == '👨‍💻 سازنده' or m.text.lower() in ['creator', 'developer'])
def creator_handler(m):
    chat_id = m.chat.id

    # مسیر عکس سازنده (فایل logo.jpg باید کنار فایل اصلی بات باشه)
    photo_path = "logo.jpg"  # اسم فایل رو هرچی خواستی بذار، مثلاً "creator.jpg"

    caption = (
        "✨ این ربات با عشق ساخته شده توسط [@Eryone0101](https://t.me/Eryone0101)\n\n"
        "📞 برای سفارش بات مشابه یا شخصی‌سازی، به من پیام بده 🌟"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("👨‍💻 مشاهده پروفایل سازنده", url="https://t.me/Eryone0101"),
        types.InlineKeyboardButton("📩 تماس با سازنده", url="https://t.me/Eryone0101")
    )

    # اگر عکس وجود داشت، با عکس بفرست
    if os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=caption, parse_mode="Markdown", reply_markup=markup)
    else:
        # اگر عکس نبود فقط پیام متنی ارسال کن
        bot.send_message(chat_id, caption, parse_mode="Markdown", reply_markup=markup)



@bot.message_handler(func=lambda m: m.text == "🌐 تغییر زبان")
def choose_lang(m):
    chat_id = m.chat.id
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🇮🇷 فارسی"), types.KeyboardButton("🇬🇧 English"), types.KeyboardButton("🇸🇦 العربية"))
    kb.add(types.KeyboardButton("🔙 بازگشت"))
    user_states[chat_id] = {"flow":"profile_edit","stage":"await_lang"}
    bot.send_message(chat_id, "زبان را انتخاب کن:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "ℹ️ درباره ما")
def about(m):
    chat_id = m.chat.id
    bot.send_message(chat_id, "🤖 این بات نسخهٔ پیشرفته است. برای پشتیبانی «🛠 پشتیبانی» را انتخاب کن.", reply_markup=main_menu_markup(chat_id))

@bot.message_handler(func=lambda m: m.text == "🛠 پشتیبانی")
def support_start(m):
    chat_id = m.chat.id
    user_states[chat_id] = {"flow":"support","stage":"await_msg"}
    bot.send_message(chat_id, get_msg(chat_id,"support_prompt"), reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.text == "📣 خبر/اعلان")
def broadcast_info(m):
    chat_id = m.chat.id
    if chat_id not in ADMIN_IDS:
        bot.send_message(chat_id, "فقط ادمین می‌تواند پیام بفرستد.", reply_markup=main_menu_markup(chat_id))
        return
    user_states[chat_id] = {"flow":"broadcast","stage":"await_broadcast"}
    bot.send_message(chat_id, "متن پیامی که می‌خواهی برای همه ارسال کنی را ارسال کن:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.text == "📱 خرید شماره مجازی")
def start_virtual(m):
    chat_id = m.chat.id
    user_states[chat_id] = {"flow":"shop","stage":"choose_type","cart": []}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(types.KeyboardButton("📱 شماره مجازی"), types.KeyboardButton("⭐ استارز"))
    kb.add(types.KeyboardButton("🧾 مشاهده سبد"), types.KeyboardButton("🔙 بازگشت"))
    bot.send_message(chat_id, "خرید: شماره یا استارز را انتخاب کن:", reply_markup=kb)

# handle quick menu choices and stateful flows
@bot.message_handler(func=lambda m: True, content_types=['text'])
def router(m):
    chat_id = m.chat.id
    text = (m.text or "").strip()
    state = user_states.get(chat_id)

    # if admin in broadcast mode
    if state and state.get("flow")=="broadcast" and state.get("stage")=="await_broadcast":
        if chat_id in ADMIN_IDS:
            msg = text
            cnt = 0
            failed = 0
            for uid in list(users_db.keys()):
                try:
                    bot.send_message(int(uid), f"📣 Broadcast:\n\n{msg}")
                    cnt += 1
                except Exception:
                    failed += 1
            broadcast_db.append({"admin":chat_id,"text":msg,"time":datetime.utcnow().isoformat(),"sent":cnt,"failed":failed})
            save_json(BROADCAST_LOG, broadcast_db)
            bot.send_message(chat_id, f"ارسال شد: {cnt} موفق / {failed} ناموفق", reply_markup=main_menu_markup(chat_id))
            user_states.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "دسترسی ندارید.", reply_markup=main_menu_markup(chat_id))
        return

    # support flow
    if state and state.get("flow")=="support" and state.get("stage")=="await_msg":
        user_states.pop(chat_id, None)
        text_msg = text
        # forward to support and admins
        try:
            bot.send_message(SUPPORT_ID, f"[Support] From {chat_id}:\n{text_msg}")
        except Exception:
            pass
        for aid in ADMIN_IDS:
            if aid == SUPPORT_ID: continue
            try:
                bot.send_message(aid, f"[Support] From {chat_id}:\n{text_msg}")
            except Exception:
                pass
        bot.send_message(chat_id, get_msg(chat_id,"support_sent"), reply_markup=main_menu_markup(chat_id))
        return

    # if no active state, handle menu buttons
    if not state:
        # main menu interactions
        if text in ["💳 کیف‌پول / شارژ","کیف‌پول","💳 کیف‌پول"]:
            user_states[chat_id] = {"flow":"wallet","stage":"menu"}
            bot.send_message(chat_id, "💼 منوی کیف پول:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("⬆️ شارژ کیف‌پول"), types.KeyboardButton("💰 مشاهده موجودی"), types.KeyboardButton("🔙 بازگشت")))
            return
        if text in ["👤 پروفایل","پروفایل"]:
            prof = user_profile(chat_id)
            txt = (
                f"👤 پروفایل شما:\n"
                f"نام: {prof.get('first_name','(ثبت نشده)')}\n"
                f"نام خانوادگی: {prof.get('last_name','(ثبت نشده)')}\n"
                f"شماره: {prof.get('phone','(ثبت نشده)')}\n"
                f"زبان: {prof.get('lang')}\n"
                f"موجودی: {prof.get('wallet',0):,} تومان\n"
                f"امتیاز: {prof.get('points',0)}\n"
                f"سطح: {'VIP' if prof.get('vip') else 'Regular'}\n"
            )
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(types.KeyboardButton("✏️ ویرایش پروفایل"), types.KeyboardButton("🌐 تغییر زبان"))
            kb.add(types.KeyboardButton("🔙 بازگشت"))
            bot.send_message(chat_id, txt, reply_markup=kb)
            return
        if text in ["⭐ خرید استارز","خرید استارز","استارز"]:
            user_states[chat_id] = {"flow":"shop","stage":"choose_stars","cart": []}
            bot.send_message(chat_id, "چند ستارز می‌خواهی؟ (حداقل {})".format(1), reply_markup=types.ReplyKeyboardRemove())
            return
        # fallback for main menu
        bot.send_message(chat_id, "از منو انتخاب کن:", reply_markup=main_menu_markup(chat_id))
        return

    # --- wallet flow ---
    if state and state.get("flow")=="wallet":
        stage = state.get("stage")
        if stage=="menu":
            if text=="⬆️ شارژ کیف‌پول":
                user_states[chat_id]["stage"]="choose_amount"
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
                kb.add(types.KeyboardButton("50,000"), types.KeyboardButton("100,000"), types.KeyboardButton("150,000"))
                kb.add(types.KeyboardButton("🔙 بازگشت"))
                bot.send_message(chat_id, "مبلغ را انتخاب کن (تومان):", reply_markup=kb)
                return
            if text=="💰 مشاهده موجودی":
                prof = user_profile(chat_id)
                bot.send_message(chat_id, get_msg(chat_id,"wallet_balance", amount=prof.get("wallet",0)), reply_markup=main_menu_markup(chat_id))
                user_states.pop(chat_id, None)
                return
        if stage=="choose_amount":
            if text=="🔙 بازگشت":
                user_states.pop(chat_id, None)
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return
            # parse number
            try:
                amt = int(text.replace(",","").strip())
            except Exception:
                bot.send_message(chat_id, "مقدار نامعتبر. یکی از گزینه‌ها را انتخاب کن.")
                return
            user_states[chat_id].update({"stage":"await_receipt","charge_amount":amt})
            bot.send_message(chat_id, get_msg(chat_id,"send_receipt"), reply_markup=types.ReplyKeyboardRemove())
            return

    # --- shop flow (numbers & stars & cart) ---
    if state and state.get("flow")=="shop":
        stage = state.get("stage")
        cart = state.get("cart", [])
        # choosing between number or stars initially
        if stage=="choose_type":
            if text in ["📱 شماره مجازی","شماره مجازی","📱"]:
                user_states[chat_id]["stage"]="choose_country"
                bot.send_message(chat_id, get_msg(chat_id,"choose_country"), reply_markup=country_choice_markup(chat_id))
                return
            if text in ["⭐ استارز","استارز","⭐"]:
                user_states[chat_id]["stage"]="choose_stars"
                bot.send_message(chat_id, "چند استارز می‌خواهی؟ (مثال: 100)", reply_markup=types.ReplyKeyboardRemove())
                return
            if text in ["🧾 مشاهده سبد","سبد","🧾 سبد خرید"]:
                if not cart:
                    bot.send_message(chat_id, get_msg(chat_id, "cart_empty"), reply_markup=main_menu_markup(chat_id))
                    user_states.pop(chat_id,None)
                    return
                summary, total = user_cart_summary(cart)
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
                kb.add(types.KeyboardButton("✅ نهایی‌سازی و پرداخت"), types.KeyboardButton("❌ خالی‌سازی سبد"))
                kb.add(types.KeyboardButton("🔙 بازگشت"))
                bot.send_message(chat_id, get_msg(chat_id,"view_cart", summary=summary, total=total), reply_markup=kb)
                user_states[chat_id]["stage"]="cart_review"
                return
            if text=="🔙 بازگشت":
                user_states.pop(chat_id,None)
                bot.send_message(chat_id, "بازگشت به منوی اصلی.", reply_markup=main_menu_markup(chat_id))
                return

        # choose_country stage: select a country to add number(s)
        if stage=="choose_country":
            if text=="🔙 بازگشت":
                user_states[chat_id]["stage"]="choose_type"
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return
            # match a country
            selected = None
            for label in COUNTRIES.keys():
                if text.startswith(label):
                    selected = label
                    break
            if not selected:
                bot.send_message(chat_id, "لطفاً از دکمه‌ها یک کشور انتخاب کن.", reply_markup=country_choice_markup(chat_id))
                return
            # ask quantity
            user_states[chat_id].update({"stage":"choose_qty","pending_country":selected,"pending_price":COUNTRIES[selected]})
            bot.send_message(chat_id, f"{selected} انتخاب شد. قیمت هر شماره: {COUNTRIES[selected]:,}\n{get_msg(chat_id,'enter_qty')}", reply_markup=qty_kb())
            return

        if stage=="choose_qty":
            if text=="🔙 بازگشت":
                user_states[chat_id]["stage"]="choose_country"
                bot.send_message(chat_id, get_msg(chat_id,"choose_country"), reply_markup=country_choice_markup(chat_id))
                return
            try:
                qty = int(text)
                if qty <= 0:
                    raise ValueError()
            except Exception:
                bot.send_message(chat_id, get_msg(chat_id,"invalid_code"))
                return
            country = state.get("pending_country")
            price = state.get("pending_price")
            # add to cart: allow multiple items of same country by appending
            cart.append({"kind":"number","country":country,"price":price,"qty":qty})
            user_states[chat_id]["cart"] = cart
            bot.send_message(chat_id, get_msg(chat_id,"cart_added"), reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("📱 ادامه خرید"), types.KeyboardButton("🧾 مشاهده سبد"), types.KeyboardButton("🔙 بازگشت")))
            user_states[chat_id]["stage"]="choose_type"
            return

        # choose_stars: adding stars into cart
        if stage=="choose_stars":
            if text=="🔙 بازگشت":
                user_states[chat_id]["stage"]="choose_type"
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return
            try:
                qty = int(text.replace(",",""))
                if qty <= 0:
                    raise ValueError()
            except Exception:
                bot.send_message(chat_id, "عدد نامعتبر. یک عدد صحیح وارد کن.")
                return
            # price per star dynamic (could be based on promotions)
            price_per = PRICE_PER_STAR
            cart.append({"kind":"stars","qty":qty,"price":price_per})
            user_states[chat_id]["cart"] = cart
            bot.send_message(chat_id, get_msg(chat_id,"cart_added"), reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("📱 ادامه خرید"), types.KeyboardButton("🧾 مشاهده سبد"), types.KeyboardButton("🔙 بازگشت")))
            user_states[chat_id]["stage"]="choose_type"
            return

        # cart review stage
        if stage=="cart_review":
            if text in ["❌ خالی‌سازی سبد","❌ Empty cart"]:
                user_states[chat_id]["cart"] = []
                bot.send_message(chat_id, "سبد خالی شد.", reply_markup=main_menu_markup(chat_id))
                user_states.pop(chat_id,None)
                return
            if text in ["✅ نهایی‌سازی و پرداخت","✅ Checkout"]:
                cart = state.get("cart",[])
                if not cart:
                    bot.send_message(chat_id, get_msg(chat_id,"cart_empty"), reply_markup=main_menu_markup(chat_id))
                    user_states.pop(chat_id,None)
                    return
                summary, total = user_cart_summary(cart)
                # require name and contact and optionally use wallet
                user_states[chat_id]["stage"]="checkout_confirm"
                user_states[chat_id]["checkout_total"]=total
                kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
                kb.add(types.KeyboardButton("💳 پرداخت با کیف‌پول"), types.KeyboardButton("📤 ارسال رسید و پرداخت دستی"))
                kb.add(types.KeyboardButton("🔙 بازگشت"))
                bot.send_message(chat_id, get_msg(chat_id,"view_cart", summary=summary, total=total), reply_markup=kb)
                return
            if text=="🔙 بازگشت":
                user_states[chat_id]["stage"]="choose_type"
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return

        # checkout confirm step
        if stage=="checkout_confirm":
            if text=="🔙 بازگشت":
                user_states[chat_id]["stage"]="choose_type"
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return
            if text=="💳 پرداخت با کیف‌پول":
                total = state.get("checkout_total",0)
                prof = user_profile(chat_id)
                if prof.get("wallet",0) >= total:
                    prof["wallet"] -= total
                    # finalize order
                    order_id = gen_order_id("ARSH-C")
                    order = {
                        "order_id": order_id,
                        "type": "checkout",
                        "cart": state.get("cart",[]),
                        "total": total,
                        "user_id": chat_id,
                        "status": "paid",
                        "time": datetime.utcnow().isoformat()
                    }
                    save_order(order)
                    # reward points and VIP
                    prof["points"] = prof.get("points",0) + int(total//10000)  # example: 1 point per 10k
                    if prof["points"] >= 100 and not prof.get("vip"):
                        prof["vip"]=True
                    set_profile(chat_id, prof)
                    bot.send_message(chat_id, f"پرداخت با کیف‌پول انجام شد. سفارش ثبت شد: {order_id}", reply_markup=main_menu_markup(chat_id))
                    # notify admins
                    for aid in ADMIN_IDS:
                        try:
                            markup = types.InlineKeyboardMarkup()
                            markup.add(types.InlineKeyboardButton("📦 مشاهده سفارش", callback_data=f"view_order:{order_id}"))
                            bot.send_message(aid, f"سفارش جدید پرداخت شده: {order_id}\nکاربر: {chat_id}\nمجموع: {total:,}", reply_markup=markup)
                        except Exception:
                            pass
                    user_states.pop(chat_id,None)
                    return
                else:
                    bot.send_message(chat_id, "موجودی کافی نیست. لطفاً کیف‌پول را شارژ کن.", reply_markup=main_menu_markup(chat_id))
                    user_states.pop(chat_id,None)
                    return
            if text=="📤 ارسال رسید و پرداخت دستی":
                # ask for receipt photo after sending contact
                user_states[chat_id]["stage"]="await_contact_for_receipt"
                bot.send_message(chat_id, get_msg(chat_id,"send_contact"), reply_markup=contact_request_kb(user_profile(chat_id).get("lang","fa")))
                return

    # profile edit flow
    if state and state.get("flow")=="profile_edit":
        stage = state.get("stage")
        if stage=="await_lang":
            if text=="🔙 بازگشت":
                user_states.pop(chat_id,None)
                bot.send_message(chat_id, "بازگشت.", reply_markup=main_menu_markup(chat_id))
                return
            lang_map = {"🇮🇷 فارسی":"fa","🇬🇧 English":"en","🇸🇦 العربية":"ar"}
            if text not in lang_map:
                bot.send_message(chat_id, "زبان نامعتبر.", reply_markup=main_menu_markup(chat_id))
                user_states.pop(chat_id,None)
                return
            prof = user_profile(chat_id)
            prof["lang"] = lang_map[text]
            set_profile(chat_id, prof)
            bot.send_message(chat_id, get_msg(chat_id,"profile_created"), reply_markup=main_menu_markup(chat_id))
            user_states.pop(chat_id,None)
            return

    # fallback
    bot.send_message(chat_id, "دستور نامشخص — از منو استفاده کن.", reply_markup=main_menu_markup(chat_id))

# contact handler (used for verification and receipts)
@bot.message_handler(content_types=['contact'])
def contact_handler(m):
    chat_id = m.chat.id
    state = user_states.get(chat_id)
    if not state:
        bot.send_message(chat_id, "ابتدا از منو گزینه‌ای انتخاب کن.", reply_markup=main_menu_markup(chat_id))
        return
    contact = m.contact
    phone = getattr(contact,"phone_number", None)
    if not phone:
        bot.send_message(chat_id, "شماره معتبر فرستاده نشده.", reply_markup=main_menu_markup(chat_id))
        return
    # profile edit finalization
    if state.get("flow")=="profile_edit" and state.get("stage")=="await_contact":
        prof = user_profile(chat_id)
        prof["phone"] = phone
        set_profile(chat_id, prof)
        bot.send_message(chat_id, get_msg(chat_id,"profile_created"), reply_markup=main_menu_markup(chat_id))
        user_states.pop(chat_id,None)
        return
    # if awaiting contact for receipt -> move to await_receipt stage and ask for photo
    if state.get("stage")=="await_contact_for_receipt":
        user_states[chat_id]["stage"]="await_receipt"
        user_states[chat_id]["receipt_phone"]=phone
        bot.send_message(chat_id, get_msg(chat_id,"send_receipt"), reply_markup=types.ReplyKeyboardRemove())
        return
    # if this is used for order verification -> create code and ask
    user_states[chat_id]["phone"] = phone
    code = gen_code()
    user_states[chat_id]["code"] = code
    user_states[chat_id]["expiry"] = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)
    user_states[chat_id]["stage"]="await_code"
    bot.send_message(chat_id, f"کد سفارش شما: {code}")
    bot.send_message(chat_id, get_msg(chat_id,"enter_code"))

# photo handler: receipts
@bot.message_handler(content_types=['photo'])
def photo_handler(m):
    chat_id = m.chat.id
    state = user_states.get(chat_id)
    if not state:
        bot.send_message(chat_id, "عکس دریافت شد اما منتظر عکس نبودیم.", reply_markup=main_menu_markup(chat_id))
        return
    if state.get("stage")=="await_receipt":
        file_id = m.photo[-1].file_id
        amount = state.get("charge_amount", 0)
        receipt_id = f"R-{datetime.utcnow().strftime('%y%m%d%H%M%S')}-{random.randint(1000,9999)}"
        rec = {"receipt_id": receipt_id, "user_id": chat_id, "file_id": file_id, "amount": amount, "time": datetime.utcnow().isoformat(), "status":"pending"}
        save_receipt(rec)
        # send to admins
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ تایید", callback_data=f"approve_receipt:{receipt_id}"))
        markup.add(types.InlineKeyboardButton("❌ رد", callback_data=f"reject_receipt:{receipt_id}"))
        for aid in ADMIN_IDS:
            try:
                bot.send_message(aid, f"🧾 رسید جدید از کاربر {chat_id}\nمقدار: {amount:,} تومان\nایدی: {receipt_id}")
                bot.send_photo(aid, file_id, reply_markup=markup)
            except Exception:
                pass
        bot.send_message(chat_id, get_msg(chat_id,"receipt_sent_admin"), reply_markup=main_menu_markup(chat_id))
        user_states.pop(chat_id,None)
        return
    bot.send_message(chat_id, "در حال حاضر تماشاگر عکس نیستیم.", reply_markup=main_menu_markup(chat_id))

# text handler for code verification (separate to avoid conflicts)
@bot.message_handler(func=lambda m: True, content_types=['text'])
def code_verification_router(m):
    # This handler only checks code if user in await_code stage
    chat_id = m.chat.id
    state = user_states.get(chat_id)
    if not state:
        return
    if state.get("stage")!="await_code":
        return
    text = (m.text or "").strip()
    expiry = state.get("expiry")
    if expiry and datetime.utcnow() > expiry:
        new_code = gen_code()
        state["code"] = new_code
        state["expiry"] = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)
        bot.send_message(chat_id, "کد قبلی منقضی شد. کد جدید ارسال شد.")
        bot.send_message(chat_id, f"کد جدید: {new_code}")
        return
    if text != state.get("code"):
        bot.send_message(chat_id, get_msg(chat_id,"invalid_code"))
        return
    # code valid -> finalize any pending order flow (if any)
    # Example: if in checkout via contact/verification, create order record
    if state.get("flow")=="shop":
        # create single-order for demonstration (earlier flows usually store cart)
        cart = state.get("cart",[])
        if not cart:
            bot.send_message(chat_id, "سبد خالی است.", reply_markup=main_menu_markup(chat_id))
            user_states.pop(chat_id,None)
            return
        order_id = gen_order_id("ARSH-V")
        order = {
            "order_id": order_id,
            "user_id": chat_id,
            "cart": cart,
            "total": state.get("checkout_total", sum(i.get("price",0)*i.get("qty",1) for i in cart)),
            "status": "pending_admin",
            "time": datetime.utcnow().isoformat()
        }
        save_order(order)
        bot.send_message(chat_id, get_msg(chat_id,"order_registered", order_id=order_id), reply_markup=main_menu_markup(chat_id))
        # notify admins
        for aid in ADMIN_IDS:
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📦 View Order", callback_data=f"view_order:{order_id}"))
                markup.add(types.InlineKeyboardButton("✅ Approve & Assign", callback_data=f"approve_order:{order_id}"))
                bot.send_message(aid, f"📦 New order {order_id}\nUser: {chat_id}\nTotal: {order['total']:,}", reply_markup=markup)
            except Exception:
                pass
    user_states.pop(chat_id,None)

# callback router for admin actions
@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    try:
        data = call.data or ""
        user_id = call.from_user.id
        # receipts
        if data.startswith("approve_receipt:") or data.startswith("reject_receipt:"):
            if user_id not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "فقط ادمین می‌تواند این کار را انجام دهد.")
                return
            action, rid = data.split(":")
            target = None
            for r in receipts_db:
                if r.get("receipt_id")==rid:
                    target = r
                    break
            if not target:
                bot.answer_callback_query(call.id, "رسید پیدا نشد.")
                return
            if action=="approve_receipt":
                uid = target["user_id"]
                prof = user_profile(uid)
                prof["wallet"] = prof.get("wallet",0) + int(target.get("amount",0))
                set_profile(uid, prof)
                target["status"]="approved"
                save_json(RECEIPTS_FILE, receipts_db)
                bot.send_message(uid, get_msg(uid,"receipt_approved", amount=target.get("amount",0)))
                bot.answer_callback_query(call.id, "رسید تایید شد.")
                try:
                    bot.edit_message_caption("✅ تایید شد", chat_id=call.message.chat.id, message_id=call.message.message_id)
                except Exception:
                    pass
                return
            else:
                target["status"]="rejected"
                save_json(RECEIPTS_FILE, receipts_db)
                bot.send_message(target["user_id"], get_msg(target["user_id"], "receipt_rejected"))
                bot.answer_callback_query(call.id, "رسید رد شد.")
                try:
                    bot.edit_message_caption("❌ رد شد", chat_id=call.message.chat.id, message_id=call.message.message_id)
                except Exception:
                    pass
                return

        # admin order actions
        if data.startswith("view_order:"):
            if user_id not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "فقط ادمین.")
                return
            _, oid = data.split(":",1)
            target = next((o for o in orders_db if o.get("order_id")==oid), None)
            if not target:
                bot.answer_callback_query(call.id, "سفارش پیدا نشد.")
                return
            bot.send_message(user_id, f"Order {oid} details:\n{json.dumps(target, ensure_ascii=False, indent=2)}")
            bot.answer_callback_query(call.id, "ارسال شد.")
            return

        if data.startswith("approve_order:"):
            if user_id not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "فقط ادمین.")
                return
            _, oid = data.split(":",1)
            target = next((o for o in orders_db if o.get("order_id")==oid), None)
            if not target:
                bot.answer_callback_query(call.id, "سفارش پیدا نشد.")
                return
            # set status to approved and optionally assign a value
            target["status"]="approved"
            save_json(ORDERS_FILE, orders_db)
            bot.send_message(user_id, f"سفارش {oid} تایید شد. می‌توانید اختصاص دهید یا اطلاعات را به کاربر ارسال کنید.")
            try:
                bot.send_message(target["user_id"], f"سفارش شما {oid} تایید شد. پس از ارسال اطلاعات، پیام می‌آید.")
            except Exception:
                pass
            bot.answer_callback_query(call.id, "تأیید شد.")
            return

    except Exception as e:
        traceback.print_exc()
        try:
            bot.answer_callback_query(call.id, "خطا در پردازش.")
        except Exception:
            pass

# run
if __name__ == "__main__":
    print("Super professional bot started...")
    bot.infinity_polling()

