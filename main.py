import requests
import os
import time
import re
from datetime import datetime

session_id = os.environ.get("IG_SESSIONID")

cookies = {'sessionid': session_id}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

print("Rakip analizi başlıyor...\n")

# Bugünün tarihini alıyoruz
tarih = datetime.now().strftime("%Y-%m-%d")

# Verileri alt alta yazacağımız tablo dosyasını (CSV) açıyoruz
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
                takipci = match.group(1)
                print(f"{hesap} sayfasının takipçi sayısı: {takipci}")
                
                # Dosyaya Tarih, Hesap Adı ve Takipçi Sayısını araya virgül koyarak yazıyoruz
                dosya_kayit.write(f"{tarih},{hesap},{takipci}\n")
            else:
                print(f"{hesap} okunamadı.")
                
            time.sleep(5)
        except Exception as e:
            print(f"Hata: {e}")

# İşimiz bitince kaydedip kapatıyoruz
dosya_kayit.close()
print("\nVeri çekme ve dosyaya yazma işlemi başarıyla tamamlandı!")
