import requests
import os
import time
import re
from datetime import datetime, timedelta

# Kasadan VIP kartımızı alıyoruz
session_id = os.environ.get("IG_SESSIONID")

cookies = {'sessionid': session_id}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

print("Rakip analizi başlıyor...\n")

# Tam olarak Türkiye saatini ayarlıyoruz
tarih = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y - %H:%M")

sonuclar = []

# Instagram'ın 866K, 1.2M veya 9,251 gibi formatlarını anlama motoru
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

# Sonuçları büyükten küçüğe sıralıyoruz
sonuclar = sorted(sonuclar, key=lambda x: x['gercek_sayi'], reverse=True)

# Vitrini (README) güncelliyoruz
readme_icerik = "# Harita Sayfaları Analiz Paneli\n\n"
readme_icerik += f"**Son Güncelleme (Türkiye Saati):** {tarih}\n\n"
readme_icerik += "| Sıra | Sayfa Adı | Takipçi Sayısı |\n"
readme_icerik += "| :---: | :--- | :---: |\n"

sira = 1
for sonuc in sonuclar:
    readme_icerik += f"| {sira} | [@{sonuc['hesap']}](https://instagram.com/{sonuc['hesap']}) | **{sonuc['takipci_metin']}** |\n"
    sira += 1

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_icerik)

print("\nVitrin başarıyla güncellendi!")
