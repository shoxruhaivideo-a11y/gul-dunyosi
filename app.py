import os
import sys

# Kutubxonani tekshirib o'rnatish
try:
    import telebot
except ImportError:
    os.system(f"{sys.executable} -m pip install pyTelegramBotAPI")
    import telebot

from telebot import types

TOKEN = "9135831262:AAH-erD3OU-TVWfTqp8HomVJjnBMwMMi-mQ"
MY_ID = 8643953727  

bot = telebot.TeleBot(TOKEN)

# DO'KONDAGI GULLAR (Telegram 100% o'qiydigan rasmlar ulandi)
PRODUCTS = {
    "1": {"name": "Oq Ayiq (Beleviy Mishka)", "price": 80000, "image": "https://picsum.photos"},
    "2": {"name": "Olovrang Xrizantema", "price": 35000, "image": "https://picsum.photos"},
    "3": {"name": "Pushti Xrizantema", "price": 35000, "image": "https://picsum.photos"}
}

user_orders = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    user_orders[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("🛒 Guldastalarni ko'rish"))
    bot.send_message(message.chat.id, "🌹 Gul Dunyosi do'konimizga xush kelibsiz!\n\nKatalogimizni ko'rish uchun quyidagi tugmani bosing:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛒 Guldastalarni ko'rish")
def show_products(message):
    bot.send_message(message.chat.id, "✨ Bizdagi mavjud guldastalar:")
    for key, prod in PRODUCTS.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=f"➕ {prod['name']}ni tanlash", callback_data=f"select_{key}"))
        bot.send_photo(chat_id=message.chat.id, photo=prod['image'], caption=f"💐 <b>{prod['name']}</b>\n💰 Narxi: {prod['price']:,} so'm", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def product_selected(call):
    chat_id = call.message.chat.id
    user_orders[chat_id]["product_key"] = call.data.split("_")[1]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1", "2", "3", "4", "5")
    bot.send_message(chat_id, "🔢 Nechta buket buyurtma qilasiz? (Raqam kiriting):", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text.isdigit() and message.chat.id in user_orders and "product_key" in user_orders[message.chat.id] and "quantity" not in user_orders[message.chat.id])
def get_quantity(message):
    chat_id = message.chat.id
    user_orders[chat_id]["quantity"] = int(message.text)
    bot.send_message(chat_id, "👤 Iltimos, ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "quantity" in user_orders[message.chat.id] and "name" not in user_orders[message.chat.id])
def get_name(message):
    chat_id = message.chat.id
    user_orders[chat_id]["name"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    bot.send_message(chat_id, "📱 Telefon raqamingizni kiriting yoki tugmani bosing:", reply_markup=markup)

@bot.message_handler(content_types=['contact', 'text'], func=lambda message: message.chat.id in user_orders and "name" in user_orders[message.chat.id] and "phone" not in user_orders[message.chat.id])
def get_phone(message):
    chat_id = message.chat.id
    user_orders[chat_id]["phone"] = message.contact.phone_number if message.content_type == 'contact' else message.text
    bot.send_message(chat_id, "📅 Buyurtma qaysi sana va soatga tayyor bo'lishi kerak?\n(Masalan: 8-noyabr soat 14:00 ga):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_orders and "phone" in user_orders[message.chat.id] and "date" not in user_orders[message.chat.id])
def get_date(message):
    chat_id = message.chat.id
    user_orders[chat_id]["date"] = message.text
    qty = user_orders[chat_id]["quantity"]
    
    if qty < 2:
        user_orders[chat_id]["delivery"] = "O'zi olib ketadi (Samovivoz — 2 tadan kam bo'lgani uchun)"
        finish_order(chat_id)
    else:
        user_orders[chat_id]["delivery"] = "Yetkazib berish (3,000 so'm/km)"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📍 Lokatsiyamni yuborish", request_location=True))
        bot.send_message(chat_id, "🚀 Siz 2 yoki undan ko'p buket tanlaganingiz uchun yetkazib berish mavjud!\n📍 Pastdagi tugma orqali lokatsiyangizni yuboring:", reply_markup=markup)

@bot.message_handler(content_types=['location'], func=lambda message: message.chat.id in user_orders and "date" in user_orders[message.chat.id])
def get_location(message):
    chat_id = message.chat.id
    user_orders[chat_id]["lat"] = message.location.latitude
    user_orders[chat_id]["lon"] = message.location.longitude
    bot.send_message(chat_id, "🗺 Do'kondan uyingizgacha necha km chiqadi? (Faqat raqam yozing, masalan: 5):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.text.isdigit() and message.chat.id in user_orders and "lat" in user_orders[message.chat.id])
def get_km(message):
    chat_id = message.chat.id
    user_orders[chat_id]["km"] = int(message.text)
    finish_order(chat_id)

def finish_order(chat_id):
    data = user_orders[chat_id]
    prod = PRODUCTS[data["product_key"]]
    total_price = prod["price"] * data["quantity"]
    delivery_text = f"🚗 {data['delivery']}"
    
    if "km" in data:
        delivery_cost = data["km"] * 3000
        total_price += delivery_cost
        delivery_text += f"\n🗺 Masofa: {data['km']} km (+{delivery_cost:,} so'm)"

    admin_text = (
        f"🔔 <b>YANGI BOTDAN BUYURTMA TUSHDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {data['name']}\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"📅 <b>Vaqti:</b> {data['date']}\n"
        f"📦 <b>Buyurtma:</b> {data['quantity']}x {prod['name']}\n"
        f"ℹ️ <b>Yetkazib berish:</b> {delivery_text}\n"
        f"💰 <b>Umumiy summa:</b> {total_price:,} so'm\n"
    )
    if "lat" in data:
        admin_text += f"\n📍 <a href='https://yandex.com{data['lon']}%2C{data['lat']}&z=15'>Yandex Xaritada ko'rish</a>"

    try:
        bot.send_photo(chat_id=MY_ID, photo=prod['image'], caption=admin_text, parse_mode="HTML")
        if "lat" in data:
            bot.send_location(chat_id=MY_ID, latitude=data["lat"], longitude=data["lon"])
        bot.send_message(chat_id, "✅ Buyurtmangiz adminga yuborildi! Rahmat!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(f"Xatolik: {e}")
    user_orders.pop(chat_id, None)

if __name__ == '__main__':
    bot.infinity_polling()
