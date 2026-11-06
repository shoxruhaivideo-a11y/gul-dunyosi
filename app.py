import os
from flask import Flask, request, render_template_string
import telebot

# Render'da xavfsiz kiritilgan muhit o'zgaruvchilarini olish
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_ID = os.environ.get('TELEGRAM_ID')

# Botni ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Avtomatik yetkazib berishni hisoblaydigan JavaScript o'rnatilgan dizayn
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
        
        .shart-blok { background: #fff9fa; border: 1px dashed #ffb6c1; padding: 10px; border-radius: 10px; font-size: 13px; margin-bottom: 15px; color: #c71585; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌸 Gul Dunyosi 🌸</h1>
        <div class="subtitle">Onlayn buyurtma va yetkazib berish</div>
        
        <div class="aloqa-blok">
            Biz bilan bog'lanish: <a href="tel:+998909180630">+998 (90) 918-06-30</a> | 
            Telegram: <a href="https://t.me" target="_blank">@Shoqqivines777</a>
        </div>

        <div class="shart-blok">
            📌 <strong>Yetkazib berish sharti:</strong> 2 ta yoki undan ko'p buket olinsa yetkazib beriladi (1 km = 3 000 so'm). 1 ta buket bo'lsa, o'zingiz olib ketasiz.
        </div>

        {% if xabar %}
            <div class="muvaffaqiyat">{{ xabar }}</div>
        {% endif %}

        <!-- Vitrina -->
        <div class="gullar-galereya">
            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Oq ayiq">
                <div>
                    <div class="gul-nomi">Oq Ayiq (Beleviy Mishka)</div>
                    <div class="narx">1 Buket: <strong>80 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>
            
            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Olovrang">
                <div>
                    <div class="gul-nomi">Olovrang Xrizantema</div>
                    <div class="narx">1 Buket: <strong>35 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>

            <div class="gul-karta">
                <img src="https://githubusercontent.com" onerror="this.src='https://unsplash.com'" alt="Pushti">
                <div>
                    <div class="gul-nomi">Pushti Xrizantema</div>
                    <div class="narx">1 Buket: <strong>35 000 so'm</strong></div>
                    <div class="tarkib">(1 ta buketda 10 dona gul)</div>
                </div>
            </div>
        </div>

        <form method="POST" action="/" id="buyurtmaForma">
            <div class="forma-guruh">
                <label for="ism">Ismingiz:</label>
                <input type="text" id="ism" name="ism" placeholder="Ismingizni kiriting..." required>
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
                <input type="number" id="soni" name="soni" value="1" min="1" onchange="tekshirBuketSoni()" required>
            </div>

            <!-- Faqat 2 ta va undan ko'p buket bo'lganda ochiladigan blok -->
            <div class="forma-guruh" id="yetkazishBlok" style="display: none;">
                <label for="km">Masofa (Necha kilometr uzoqlikda joylashgansiz?):</label>
                <input type="number" id="km" name="km" value="0" min="0" placeholder="Masalan: 5">
                <p style="font-size: 12px; color: #28a745; margin-top: 5px;">🚗 Yetkazib berish: 1 km = 3,000 so'm qo'shiladi.</p>
            </div>

            <div class="forma-guruh" id="oziOlibKetishMatn">
                <p style="color: #dc3545; font-size: 14px; font-weight: bold;">⚠️ 1 ta buket uchun yetkazib berish mavjud emas. Faqat o'zingiz olib ketishingiz (Samovivoz) mumkin.</p>
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
                <label for="izoh">Yetkazish manzili yoki qo'shimcha istaklar:</label>
                <textarea id="izoh" name="izoh" rows="3" placeholder="Masalan: Uy raqami, lenta rangi va hokazo..."></textarea>
            </div>

            <button type="submit">🌸 Buyurtma berish 🌸</button>
        </form>
    </div>

    <script>
        function tekshirBuketSoni() {
            var soni = document.getElementById("soni").value;
            var yetkazishBlok = document.getElementById("yetkazishBlok");
            var oziOlibKetishMatn = document.getElementById("oziOlibKetishMatn");
            var kmInput = document.getElementById("km");
            
            if (soni >= 2) {
                yetkazishBlok.style.display = "block";
                oziOlibKetishMatn.style.display = "none";
                kmInput.required = true;
            } else {
                yetkazishBlok.style.display = "none";
                oziOlibKetishMatn.style.display = "block";
                kmInput.value = 0;
                kmInput.required = false;
            }
        }
        // Sahifa yuklanganda bir marta tekshirib oladi
        tekshirBuketSoni();
    </script>
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
        km = int(request.form.get("km", 0))
        sana = request.form.get("sana")
        telefon = request.form.get("telefon")
        izoh = request.form.get("izoh", "Yo'q")
        
        # Buket narxlari
        if gul_turi == "Oq Ayiq (Beleviy Mishka) Buketi":
            bitta_buket_narxi = 80000
        else:
            bitta_buket_narxi = 35000
            
        gullar_narxi = soni * bitta_buket_narxi
        
        # Yetkazish xizmatini hisoblash (Faqat 2 ta va undan ko'p buket uchun)
        if soni >= 2:
            yetkazish_narxi = km * 3000
            umumiy_narx = gullar_narxi + yetkazish_narxi
