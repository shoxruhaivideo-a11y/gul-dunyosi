import os
import sys

# Kerakli kutubxonalarni o'rnatamiz
os.system(f"{sys.executable} -m pip install pyTelegramBotAPI")
import telebot
from telebot import types

TOKEN = "9135831262:AAH-erD3OU-TVWfTqp8HomVJjnBMwMMi-mQ"
MY_ID = 8643953727  

bot = telebot.TeleBot(TOKEN)

# Do'kondagi 3 ta guldasta ma'lumotlari (Rasm, Nom va Narx)
PRODUCTS = {
    "1": {"name": "Qizil Atirgullar", "price": 150000, "image": "https://unsplash.com"},
    "2": {"name": "Oq Lilliyalar", "price": 180000, "image": "https://unsplash.com"},
    "3": {"name": "Mikst Guldasta", "price": 220000, "image": "https://unsplash.com"}
}

# Mijozlar buyurtma jarayonini saqlash uchun vaqtinchalik baza
user_orders = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    user_orders[message.chat.id] = {} # Yangi buyurtma boshlash
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("🛒 Guldastalarni ko'rish"))
    
    bot.send_message(
        message.chat.id, 
        "🌹 Gul Dunyosi do'konimizga xush kelibsiz!\n\nKatalogimizni ko'rish uchun quyidagi tugmani bosing:", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🛒 Guldastalarni ko'rish")
def show_products(message):
    bot.send_message(message.chat.id, "✨ Bizdagi mavjud guldastalar:")
    
    # 3 ta gulni rasmi va narxi bilan mijozga ko'rsatamiz
    for key, prod in PRODUCTS.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=f"➕ {prod['name']}ni tanlash", callback_data=f"select_{key}"))
        
        bot.send_photo(
            chat_id=message.chat.id,
            photo=prod['image'],
            caption=f"💐 <b>{prod['name']}</b>\n💰 Narxi: {prod['price']:,} so'm",
            parse_mode="HTML",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def product_selected(call):
    prod_key = call.data.split("_")[1]
    user_orders[call.message.chat.id]["product_key"] = prod_key
    
    # Soni so'rash uchun tugmalar
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1", "2", "3", "4", "5")
    
    bot.send_message(call.message.chat.id, "🔢 Nechta buket buyurtma qilasiz? (Raqam kiriting):", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in ["1", "2", "3", "4", "5"] or message.text.isdigit())
def get_quantity(message):
    chat_id = message.chat.id
    if chat_id not in user_orders or "product_key" not in user_orders[chat_id]:
        return
        
    qty = int(message.text)
    user_orders[chat_id]["quantity"] = qty
    
    # Ismini so'raymiz
    bot.send_message(chat_id, "👤 Iltimos, ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "quantity" in user_orders[message.chat.id] and "name" not in user_orders[message.chat.id])
def get_name(message):
    chat_id = message.chat.id
    user_orders[chat_id]["name"] = message.text
    
    # Telefon raqam so'rash
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    
    bot.send_message(chat_id, "📱 Telefon raqamingizni yuboring (yoki yozing):", reply_markup=markup)

@bot.message_handler(content_types=['contact', 'text'], func=lambda message: message.chat.id in user_orders and "name" in user_orders[message.chat.id] and "phone" not in user_orders[message.chat.id])
def get_phone(message):
    chat_id = message.chat.id
    if message.content_type == 'contact':
        user_orders[chat_id]["phone"] = message.contact.phone_number
    else:
        user_orders[chat_id]["phone"] = message.text
        
    bot.send_message(chat_id, "📅 Buyurtma qaysi sana va soatga tayyor bo'lishi kerak? (Masalan: 8-noyabr soat 14:00 ga):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "phone" in user_orders[message.chat.id] and "date" not in user_orders[message.chat.id])
def get_date(message):
    chat_id = message.chat.id
    user_orders[chat_id]["date"] = message.text
    
    qty = user_orders[chat_id]["quantity"]
    
    # 2 tadan kam bo'lsa - O'zi olib ketadi
    if qty < 2:
        user_orders[chat_id]["delivery"] = "O'zi olib ketadi (2 tadan kam bo'lgani uchun)"
        finish_order(chat_id)
    else:
        # 2 ta va undan ko'p bo'lsa - Lokatsiya so'raymiz
        user_orders[chat_id]["delivery"] = "Yetkazib berish (3,000 so'm/km)"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📍 Lokatsiyamni yuborish", request_location=True))
        bot.send_message(chat_id, "🚀 Siz 2 yoki undan ko'p buket tanlaganingiz uchun yetkazib berish mavjud!\n📍 Iltimos, lokatsiyangizni yuboring:", reply_markup=markup)

@bot.message_handler(content_types=['location'], func=lambda message: message.chat.id in user_orders and "date" in user_orders[message.chat.id])
def get_location(message):
    chat_id = message.chat.id
    user_orders[chat_id]["lat"] = message.location.latitude
    user_orders[chat_id]["lon"] = message.location.longitude
    finish_order(chat_id)

def finish_order(chat_id):
    data = user_orders[chat_id]
    prod = PRODUCTS[data["product_key"]]
    total_price = prod["price"] * data["quantity"]
    
    # Do'kondan uzoqlikni hisoblash (Namuna sifatida 5 km olingan, real loyihada Yandex API masofani aniqlaydi)
    delivery_text = f"🚗 {data['delivery']}"
    if "lat" in data:
        distance = 5 # Taxminiy masofa (km)
        delivery_cost = distance * 3000
        total_price += delivery_cost
        delivery_text += f"\n🗺 Taxminiy masofa: {distance} km (+{delivery_cost:,} so'm)"

    # Adminga (SIZGA) boradigan yakuniy SMS-Xabar matni
    admin_text = (
        f"🔔 <b>YANGI BUYURTMA TUSHDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {data['name']}\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"📅 <b>Vaqti:</b> {data['date']}\n"
        f"📦 <b>Mahsulot:</b> {data['quantity']}x {prod['name']}\n"
        f"ℹ️ <b>Yetkazib berish:</b> {delivery_text}\n"
        f"💰 <b>Umumiy summa:</b> {total_price:,} so'm\n"
    )
    
    if "lat" in data:
        admin_text += f"\n📍 <a href='https://yandex.com{data['lon']}%2C{data['lat']}&z=15'>Yandex Xaritada ko'rish</a>"

    try:
        # SIZGA tanlangan gulning rasmi va barcha ma'lumotlar boradi
        bot.send_photo(chat_id=MY_ID, photo=prod['image'], caption=admin_text, parse_mode="HTML")
        if "lat" in data:
            bot.send_location(chat_id=MY_ID, latitude=data["lat"], longitude=data["lon"])
            
        # Mijozga rahmatnoma
        bot.send_message(chat_id, "✅ Buyurtmangiz qabul qilindi va adminga yuborildi! Rahmat!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(f"Xatolik: {e}")
        
    # Amaldagi buyurtmani tozalaymiz
    user_orders.pop(chat_id, None)

if __name__ == '__main__':
    bot.infinity_polling()
