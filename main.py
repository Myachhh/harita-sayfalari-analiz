import requests
import os
import time
import re
from datetime import datetime, timedelta

session_id = os.environ.get("IG_SESSIONID")

cookies = {'sessionid': session_id}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

print("Rakip analizi ve Web Paneli hazırlığı başlıyor...\n")

tarih = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y - %H:%M")
sonuclar = []

def sayiya_cevir(metin):
    m = metin.upper().replace(',', '')
    try:
        if 'K' in m: return int(float(m.replace('K', '')) * 1000)
        if 'M' in m: return int(float(m.replace('M', '')) * 1000000)
        return int(m)
    except:
        return 0

dosya_kayit = open("takipciler.csv", "a", encoding="utf-8")

with open("hesaplar.txt", "r") as dosya:
    hesaplar = dosya.read().splitlines()

for hesap in hesaplar:
    hesap = hesap.strip()
    if hesap: 
        try:
            url = f"https://www.instagram.com/{hesap}/"
            response = requests.get(url, cookies=cookies, headers=headers)
            match = re.search(r'content="([^"]+?)\s+Followers', response.text)
            
            if match:
                takipci_metin = match.group(1)
                gercek_sayi = sayiya_cevir(takipci_metin)
                
                print(f"{hesap}: {takipci_metin}")
                dosya_kayit.write(f"{tarih},{hesap},{takipci_metin}\n")
                
                sonuclar.append({
                    "hesap": hesap,
                    "takipci_metin": takipci_metin,
                    "gercek_sayi": gercek_sayi
                })
            else:
                print(f"{hesap} okunamadı.")
            time.sleep(5)
        except Exception as e:
            print(f"Hata: {e}")

dosya_kayit.close()

# Büyükten küçüğe sıralama
sonuclar = sorted(sonuclar, key=lambda x: x['gercek_sayi'], reverse=True)

# 1. README.md Güncelleme
readme_icerik = "# Harita Sayfaları Analiz Paneli\n\n"
readme_icerik += f"**Son Güncelleme:** {tarih}\n\n"
readme_icerik += "| Sıra | Sayfa Adı | Takipçi Sayısı |\n"
readme_icerik += "| :---: | :--- | :---: |\n"
sira = 1
for sonuc in sonuclar:
    readme_icerik += f"| {sira} | [@{sonuc['hesap']}](https://instagram.com/{sonuc['hesap']}) | **{sonuc['takipci_metin']}** |\n"
    sira += 1
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_icerik)

# 2. ŞIK VE MODERN WEB SİTESİ (index.html) ÜRETME
html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harita Sayfaları Analiz Paneli</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            width: 100%;
            max-width: 800px;
        }}
        h1 {{
            color: #58a6ff;
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .guncelleme {{
            color: #8b949e;
            font-size: 14px;
            margin-bottom: 30px;
            background: #161b22;
            padding: 10px 15px;
            border-radius: 6px;
            display: inline-block;
            border: 1px solid #30363d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #161b22;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #30363d;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
        }}
        th {{
            background-color: #21262d;
            color: #f0f6fc;
            font-weight: 600;
            border-bottom: 2px solid #30363d;
        }}
        tr {{
            border-bottom: 1px solid #30363d;
        }}
        tr:last-child {{
            border-bottom: none;
        }}
        tr:hover {{
            background-color: #1f242c;
        }}
        .sira {{
            font-weight: bold;
            color: #8b949e;
            width: 50px;
            text-align: center;
        }}
        .link {{
            color: #58a6ff;
            text-decoration: none;
            font-weight: 500;
        }}
        .link:hover {{
            text-decoration: underline;
        }}
        .sayi {{
            font-weight: 700;
            color: #56d364;
            text-align: right;
        }}
        th.sag, td.sag {{
            text-align: right;
        }}
        th.orta, td.orta {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 Harita Sayfaları Analiz Paneli</h1>
        <div class="guncelleme">🔄 Son Güncelleme (TSİ): {tarih}</div>
        
        <table>
            <thead>
                <tr>
                    <th class="orta">Sıra</th>
                    <th>Sayfa Adı</th>
                    <th class="sag">Takipçi Sayısı</th>
                </tr>
            </thead>
            <tbody>
"""

sira = 1
for sonuc in sonuclar:
    html_icerik += f"""                <tr>
                    <td class="orta sira">{sira}</td>
                    <td><a class="link" href="https://instagram.com/{sonuc['hesap']}" target="_blank">@{sonuc['hesap']}</a></td>
                    <td class="sag sayi">{sonuc['takipci_metin']}</td>
                </tr>\n"""
    sira += 1

html_icerik += """            </tbody>
        </table>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)

print("\nWeb sitesi (index.html) başarıyla üretildi!")
