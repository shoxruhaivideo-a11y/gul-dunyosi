import os
from flask import Flask, request, render_template_string
import telebot

# Render'da xavfsiz kiritilgan muhit o'zgaruvchilarini olish
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_ID = os.environ.get('TELEGRAM_ID')

# Botni ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Faqat tayyor buketlar (1 ta buket = 10 ta gul) tizimidagi yakuniy dizayn
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
        
        .gullar-galereya { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
        @media (max-width: 500px) { .gullar-galereya { grid-template-columns: 1fr; } }
        
        .gul-karta { border: 2px solid #ffb6c1; border-radius: 15px; padding: 15px; text-align: center; background: #fffdfd; display: flex; flex-direction: column; justify-content: space-between; }
        .gul-karta img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }
        .gul-nomi { font-size: 16px; font-weight: bold; color: #db7093; margin: 10px 0 5px 0; }
        .narx { font-size: 13px; margin: 3px 0; color: #555; }
        .narx strong { color: #ff1493; }
        .tarkib { font-size: 12px; color: #777; font-style: italic; }
        
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
        <div class="subtitle">Sizning shaxsiy onlayn gullar do'koningiz</div>
        
        <div class="aloqa-blok">
            Biz bilan bog'lanish: <a href="tel:+998909180630">+998 (90) 918-06-30</a> | 
            Telegram: <a href="https://t.me" target="_blank">@Shoqqivines777</a>
        </div>

        {% if xabar %}
            <div class="muvaffaqiyat">{{ xabar }}</div>
        {% endif %}

        <!-- Vitrina -->
        <div class="gullar-galereya">
            <!-- 1. Oq ayiq -->
            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Oq ayiq">
                <div>
                    <div class="gul-nomi">Oq Ayiq (Beleviy Mishka)</div>
                    <div class="narx">1 Buket: <strong>80 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>
            
            <!-- 2. Olovrang -->
            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Olovrang">
                <div>
                    <div class="gul-nomi">Olovrang Xrizantema</div>
                    <div class="narx">1 Buket: <strong>35 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>

            <!-- 3. Pushti -->
            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Pushti">
                <div>
                    <div class="gul-nomi">Pushti Xrizantema</div>
                    <div class="narx">1 Buket: <strong>35 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>
        </div>

        <form method="POST" action="/">
            <div class="forma-guruh">
                <label for="ism">Ismingiz:</label>
                <input type="text" id="ism" name="ism" placeholder="Ismingizni kiriting...">
            </div>

            <div class="forma-guruh">
                <label for="gul_turi">Buket turini tanlang:</label>
                <select id="gul_turi" name="gul_turi">
                    <option value="Oq Ayiq (Beleviy Mishka) Buketi">Oq Ayiq (Beleviy Mishka) — 80,000 so'm</option>
                    <option value="Olovrang xrizantema buketi">Olovrang xrizantema — 35,000 so'm</option>
                    <option value="Pushti xrizantema buketi">Pushti xrizantema — 35,000 so'm</option>
                </select>
            </div>

            <div class="forma-guruh">
                <label for="soni">Nechta buket kerak?</label>
                <input type="number" id="soni" name="soni" value="1" min="1" required>
            </div>

            <div class="forma-guruh">
                <label for="sana">Qaysi kunga kerak?</label>
                <input type="date" id="sana" name="sana" required>
            </div>

            <div class="forma-guruh">
                <label for="telefon">Telefon raqamingiz</label>
                <input type="tel" id="telefon" name="telefon" placeholder="+998 90 123 45 67" value="+998" required>
            </div>

            <div class="forma-guruh">
                <label for="izoh">Qo'shimcha istaklaringiz:</label>
                <textarea id="izoh" name="izoh" rows="3" placeholder="Masalan: lenta rangi yoki yetkazib berish manzili..."></textarea>
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
        ism = request.form.get("ism", "Kiritilmagan")
        gul_turi = request.form.get("gul_turi")
        soni = int(request.form.get("soni", 1))
        sana = request.form.get("sana")
        telefon = request.form.get("telefon")
        izoh = request.form.get("izoh", "Yo'q")
        
        # Aniq buket narxlari (35,000 va 80,000)
        if gul_turi == "Oq Ayiq (Beleviy Mishka) Buketi":
            bitta_buket_narxi = 80000
        else:
            bitta_buket_narxi = 35000
            
        umumiy_narx = soni * bitta_buket_narxi
        narx_matni = f"{umumiy_narx:,} so'm"
        
        telegram_xabari = (
            f"🛍 **YANGI BUYURTMA KELDI!**\n\n"
            f"👤 **Mijoz ismi:** {ism}\n"
            f"💐 **Gul turi:** {gul_turi}\n"
            f"🔢 **Buket soni:** {soni} ta buket (har birida 10 tadan gul)\n"
            f"💰 **Umumiy narx:** {narx_matni}\n"
            f"📅 **Qachonga:** {sana}\n"
            f"📞 **Telefon:** {telefon}\n"
            f"✍️ **Izoh:** {izoh}"
        )
        
        try:
            bot.send_message(TELEGRAM_ID, telegram_xabari, parse_mode="Markdown")
            xabar = "Rahmat! Buyurtmangiz muvaffaqiyatli qabul qilindi va do'kon egasiga yuborildi."
        except Exception as e:
            xabar = f"Xatolik yuz berdi: {str(e)}"
            
    return render_template_string(SAYT_DIZAYNI, xabar=xabar)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
