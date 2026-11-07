import os
import sys

# Render serverida kutubxonani avtomatik o'rnatish
os.system(f"{sys.executable} -m pip install pyTelegramBotAPI")
import telebot

TOKEN = "9135831262:AAH-erD3OU-TVWfTqp8HomVJjnBMwMMi-mQ"
MY_ID = 8643953727  

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = telebot.types.KeyboardButton("🛍 Buyurtma berish")
    markup.add(btn)
    bot.send_message(
        message.chat.id, 
        "🌹 Gul Dunyosi do'konimizga xush kelibsiz!\n\nBuyurtma berish uchun quyidagi tugmani bosing:", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🛍 Buyurtma berish")
def handle_order(message):
    tekst = (
        f"🔔 <b>YANGI GUL BUYURTMASI TUSHDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {message.from_user.full_name}\n"
        f"📦 <b>Mahsulot:</b> 1x Qizil Atirgullar guldastasi\n"
        f"💰 <b>Summa:</b> 150,000 so'm\n\n"
        f"📍 <a href='https://yandex.com'>Yandex Xaritada ko'rish</a>"
    )
    try:
        rasm_url = "https://unsplash.com"
        bot.send_photo(chat_id=MY_ID, photo=rasm_url, caption=tekst, parse_mode="HTML")
        bot.send_location(chat_id=MY_ID, latitude=41.311081, longitude=69.240562)
        bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi! Tez orada administrator bog'lanadi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik: {e}")

if __name__ == '__main__':
    print("Gul Dunyosi Boti muvaffaqiyatli yoqildi!")
    bot.infinity_polling()
