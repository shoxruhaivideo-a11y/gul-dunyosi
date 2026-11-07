import os
import sys

# Kutubxonani avtomatik o'rnatish
try:
    import telebot
except ImportError:
    os.system(f"{sys.executable} -m pip install pyTelegramBotAPI")
    import telebot

from telebot import types

TOKEN = "9135831262:AAH-erD3OU-TVWfTqp8HomVJjnBMwMMi-mQ"
MY_ID = 8643953727  

bot = telebot.TeleBot(TOKEN)

# Do'kondagi 3 ta guldasta ma'lumotlari (Bloklanmaydigan ishonchli rasmlar)
PRODUCTS = {
    "1": {"name": "Oq Ayiq (Beleviy Mishka)", "price": 80000, "image": "https://googleusercontent.com"},
    "2": {"name": "Olovrang Xrizantema", "price": 35000, "image": "https://googleusercontent.com"},
    "3": {"name": "Pushti Xrizantema", "price": 35000, "image": "https://googleusercontent.com"}
}

# Mijozlar buyurtma ma'lumotlarini vaqtincha saqlash xotirasi
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
    
    # 3 ta gulni rasmi va narxi bilan mijozga navbat bilan ko'rsatamiz
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
    chat_id = call.message.chat.id
    prod_key = call.data.split("_")[1]
    
    user_orders[chat_id]["product_key"] = prod_key
    
    # Soni so'rash uchun tugmalar
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1", "2", "3", "4", "5")
    
    bot.send_message(chat_id, f"🔢 Nechta buket buyurtma qilasiz? (Raqam kiriting):", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text.isdigit() and message.chat.id in user_orders and "product_key" in user_orders[message.chat.id] and "quantity" not in user_orders[message.chat.id])
def get_quantity(message):
    chat_id = message.chat.id
    qty = int(message.text)
    user_orders[chat_id]["quantity"] = qty
    
    bot.send_message(chat_id, "👤 Iltimos, ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "quantity" in user_orders[message.chat.id] and "name" not in user_orders[message.chat.id])
def get_name(message):
    chat_id = message.chat.id
    user_orders[chat_id]["name"] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    
    bot.send_message(chat_id, "📱 Telefon raqamingizni kiriting yoki quyidagi tugmani bosing:", reply_markup=markup)

@bot.message_handler(content_types=['contact', 'text'], func=lambda message: message.chat.id in user_orders and "name" in user_orders[message.chat.id] and "phone" not in user_orders[message.chat.id])
def get_phone(message):
    chat_id = message.chat.id
    if message.content_type == 'contact':
        user_orders[chat_id]["phone"] = message.contact.phone_number
    else:
        user_orders[chat_id]["phone"] = message.text
        
    bot.send_message(chat_id, "📅 Buyurtma qaysi sana va soatga tayyor bo'lishi kerak?\n(Masalan: 8-noyabr soat 14:00 ga):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "phone" in user_orders[message.chat.id] and "date" not in user_orders[message.chat.id])
def get_date(message):
    chat_id = message.chat.id
    user_orders[chat_id]["date"] = message.text
    
    qty = user_orders[chat_id]["quantity"]
    
    # QOIDA: 2 tadan kam bo'lsa (1 ta bo'lsa) - Faqat o'zi olib ketadi (Samovivoz)
    if qty < 2:
        user_orders[chat_id]["delivery"] = "O'zi olib ketadi (Samovivoz — 2 tadan kam bo'lgani uchun)"
        finish_order(chat_id)
    else:
        # QOIDA: 2 ta va undan ko'p bo'lsa - Lokatsiya so'raymiz
        user_orders[chat_id]["delivery"] = "Yetkazib berish (3,000 so'm/km)"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📍 Lokatsiyamni yuborish", request_location=True))
        
        bot.send_message(
            chat_id, 
            "🚀 Siz 2 yoki undan ko'p buket tanlaganingiz uchun yetkazib berish xizmati mavjud!\n\n📍 Iltimos, pastdagi tugma orqali lokatsiyangizni yuboring:", 
            reply_markup=markup
        )

@bot.message_handler(content_types=['location'], func=lambda message: message.chat.id in user_orders and "date" in user_orders[message.chat.id])
def get_location(message):
    chat_id = message.chat.id
    user_orders[chat_id]["lat"] = message.location.latitude
    user_orders[chat_id]["lon"] = message.location.longitude
    
    # Masofani so'raymiz (Klometrni aniqlash uchun)
    bot.send_message(chat_id, "🗺 Do'kondan uyingizgacha necha kilometr chiqadi? (Faqat raqam yozing, masalan: 5):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text.isdigit() and message.chat.id in user_orders and "lat" in user_orders[message.chat.id])
def get_km(message):
    chat_id = message.chat.id
    user_orders[chat_id]["km"] = int(message.text)
    finish_order(chat_id)

def finish_order(chat_id):
    data = user_orders[chat_id]
    prod = PRODUCTS[data["product_key"]]
    
    # Hisob-kitob qismi
    gul_narxi = prod["price"] * data["quantity"]
    total_price = gul_narxi
    
    delivery_text = f"🚗 {data['delivery']}"
    
    # Agar yetkazib berish bo'lsa kilometrini hisoblaymiz (1km = 3000 so'm)
    if "km" in data:
        delivery_cost = data["km"] * 3000
        total_price += delivery_cost
        delivery_text += f"\n🗺 Masofa: {data['km']} km (+{delivery_cost:,} so'm)"

    # SIZGA (Adminga) boradigan SMS-Xabar matni
    admin_text = (
        f"🔔 <b>YANGI BOTDAN BUYURTMA TUSHDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {data['name']}\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"📅 <b>Tayyor bo'lish vaqti:</b> {data['date']}\n"
        f"📦 <b>Buyurtma:</b> {data['quantity']}x {prod['name']}\n"
        f"ℹ️ <b>Yetkazib berish:</b> {delivery_text}\n"
        f"💰 <b>Umumiy summa:</b> {total_price:,} so'm\n"
    )
    
    if "lat" in data:
        admin_text += f"\n📍 <a href='https://yandex.com{data['lon']}%2C{data['lat']}&z=15'>Yandex Xaritada ko'rish</a>"

    try:
        # 1. SIZGA (MY_ID raqamiga) tanlangan gulning rasmi va barcha ma'lumotlar birga boradi
        bot.send_photo(chat_id=MY_ID, photo=prod['image'], caption=admin_text, parse_mode="HTML")
        
        # 2. Agar lokatsiya yuborgan bo'lsa, xaritada ham keladi
        if "lat" in data:
            bot.send_location(chat_id=MY_ID, latitude=data["lat"], longitude=data["lon"])
            
        # Mijozning o'ziga buyurtma tugagani haqida javob
        bot.send_message(chat_id, "✅ Buyurtmangiz qabul qilindi va adminga yuborildi! Tez orada aloqaga chiqamiz, rahmat!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(f"Xabarni adminga yuborishda xatolik: {e}")
        
    # Amaldagi buyurtma tugadi, xotirani tozalaymiz
    user_orders.pop(chat_id, None)

if __name__ == '__main__':
    print("Gul Dunyosi Bot to'liq yoqildi!")
    bot.infinity_polling()
