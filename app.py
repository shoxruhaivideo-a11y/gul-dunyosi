import os
from flask import Flask, request, render_template_string
import telebot

# Render'da xavfsiz kiritgan muhit o'zgaruvchilarini olish
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_ID = os.environ.get('TELEGRAM_ID')

# Botni ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Pushti rangdagi zamonaviy va telefonbop sayt dizayni (HTML/CSS)
SAYT_DIZAYNI = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gul Dunyosi — Onlayn do'kon</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #fff0f5; color: #4a4a4a; margin: 0; padding: 20px; }
        .container { max-width: 600px; background: white; margin: 0 auto; padding: 25px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
        h1 { color: #ff69b4; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #db7093; font-style: italic; margin-bottom: 25px; }
        .aloqa-blok { text-align: center; background: #ffe4e1; padding: 10px; border-radius: 10px; margin-bottom: 25px; font-size: 14px; }
        .aloqa-blok a { color: #db7093; text-decoration: none; font-weight: bold; }
        .gul-karta { border: 2px solid #ffb6c1; border-radius: 15px; padding: 15px; margin-bottom: 25px; text-align: center; background: #fffdfd; }
        .gul-karta img { max-width: 100%; height: auto; border-radius: 10px; max-height: 25px0px; }
        .gul-nomi { font-size: 22px; font-weight: bold; color: #db7093; margin: 10px 0; }
        .narx { font-size: 16px; margin: 5px 0; color: #555; }
        .narx strong { color: #ff1493; }
        .forma-guruh { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #db7093; }
        input, textarea, select { width: 100%; padding: 12px; border: 1px solid #ffb6c1; border-radius: 10px; box-sizing: border-box; font-size: 15px; background-color: #fff0f5; }
        input:focus, textarea:focus, select:focus { outline: none; border-color: #ff69b4; background-color: #fff; }
        button { width: 100%; background: #ff69b4; color: white; border: none; padding: 15px; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 10px rgba(255,105,180,0.3); }
        button:hover { background: #db7093; }
        .muvaffaqiyat { background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌸 Gul Dunyosi 🌸</h1>
        <div class="subtitle">Zamonaviy onlayn gullar do'koni</div>
        
        <div class="aloqa-blok">
            Biz bilan bog'lanish: <a href="tel:+998909180630">+998 (90) 918-06-30</a> | 
            Telegram: <a href="https://t.me" target="_blank">@Shoqqivines777</a>
        </div>

        {% if xabar %}
            <div class="muvaffaqiyat">{{ xabar }}</div>
        {% endif %}

        <form method="POST" action="/">
            <div class="gul-karta">
                <!-- Chiroyli pushti gul rasmi -->
                <img src="https://unsplash.com" alt="Pushti xrizantema buket">
                <div class="gul-nomi">Pushti Xrizantema Buketi</div>
                <p style="font-size: 14px; color: #777; margin: 0 0 10px 0;">Mayin pushti va to'q pushti gullar aralashtirilgan nafis va jozibali buket.</p>
                <div class="narx">1 dona gul: <strong>2 000 so'm</strong></div>
                <div class="narx">15 dona gul (Buket): <strong>30 000 so'm</strong></div>
            </div>

            <div class="forma-guruh">
                <label for="ism">Ismingiz:</label>
                <input type="text" id="ism" name="ism" placeholder="Ismingizni kiriting...">
            </div>

            <div class="forma-guruh">
                <label for="gul_turi">Gul turi:</label>
                <select id="gul_turi" name="gul_turi">
                    <option value="Mayin pushti va pushti gullar aralash buketi">Mayin pushti va pushti gullar aralash buketi</option>
                    <option value="Oppoq xrizantema (Narxi belgilanish arafasida)">Oppoq xrizantema (Narxi belgilanmagan)</option>
                </select>
            </div>

            <div class="forma-guruh">
                <label for="soni">Nechta gul kerak (dona):</label>
                <input type="number" id="soni" name="soni" value="15" min="1" required>
            </div>

            <div class="forma-guruh">
                <label for="sana">Yetkazib berish sanasi:</label>
                <input type="date" id="sana" name="sana" required>
            </div>

            <div class="forma-guruh">
                <label for="telefon">Telefon raqamingiz:</label>
                <input type="tel" id="telefon" name="telefon" value="+998" required>
            </div>

            <div class="forma-guruh">
                <label for="izoh">Qo'shimcha izoh yoki istaklar:</label>
                <textarea id="izoh" name="izoh" rows="3" placeholder="Masalan: chiroyli qadoqlansin..."></textarea>
            </div>

            <button type="submit">🌸 Buyurtma berish 🌸</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    xabar = None
    if request.method == "POST":
        # Formadan ma'lumotlarni yig'ib olish
        ism = request.form.get("ism", "Kiritilmagan")
        gul_turi = request.form.get("gul_turi")
        soni = int(request.form.get("soni", 1))
        sana = request.form.get("sana")
        telefon = request.form.get("telefon")
        izoh = request.form.get("izoh", "Yo'q")
        
        # Narxni hisoblash (Pushti gullar uchun 2000 so'mdan)
        umumiy_narx = soni * 2000
        
        # Telegram xabari formatini chiroyli qilish
        telegram_xabari = (
            f"🛍 **YANGI BUYURTMA KELDI!**\n\n"
            f"👤 **Mijoz ismi:** {ism}\n"
            f"💐 **Gul turi:** {gul_turi}\n"
            f"🔢 **Soni:** {soni} dona\n"
            f"💰 **Umumiy narx:** {umumiy_narx:,} so'm\n"
            f"📅 **Sana:** {sana}\n"
            f"📞 **Telefon:** {telefon}\n"
            f"✍️ **Izoh:** {izoh}"
        )
        
        # Telegram bot orqali sizning ID raqamingizga xabar jo'natish
        try:
            bot.send_message(TELEGRAM_ID, telegram_xabari, parse_mode="Markdown")
            xabar = "Rahmat! Buyurtmangiz muvaffaqiyatli qabul qilindi va do'kon egasiga yuborildi."
        except Exception as e:
            xabar = f"Xatolik yuz berdi, buyurtma bot orqali ketmadi: {str(e)}"
            
    return render_template_string(SAYT_DIZAYNI, xabar=xabar)

if __name__ == "__main__":
    # Render portni avtomatik beradi
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
