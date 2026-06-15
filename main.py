import requests
import os
import time
import re

# Kasadan VIP kartımızı alıyoruz
session_id = os.environ.get("IG_SESSIONID")

print("Rakip analizi başlıyor...\n")

# Sanki bilgisayardan giriyormuşuz gibi davranmak için ayarlar
cookies = {'sessionid': session_id}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Hesap listesini okuyoruz
with open("hesaplar.txt", "r") as dosya:
    hesaplar = dosya.read().splitlines()

for hesap in hesaplar:
    hesap = hesap.strip()
    if hesap: 
        try:
            url = f"https://www.instagram.com/{hesap}/"
            # Sayfaya normal bir giriş yapıyoruz
            response = requests.get(url, cookies=cookies, headers=headers)
            
            # Sayfanın arka planındaki metinlerden takipçi sayısını cımbızla çekiyoruz
            match = re.search(r'content="([^"]+?)\s+Followers', response.text)
            
            if match:
                takipci = match.group(1)
                print(f"{hesap} sayfasının takipçi sayısı: {takipci}")
            else:
                print(f"{hesap} sayfası okundu ama sayı bulunamadı. (Gizli profil olabilir)")
                
            # Engel yememek için 5 saniye bekleme
            time.sleep(5)
        except Exception as e:
            print(f"{hesap} sayfası için hata: {e}")

print("\nVeri çekme işlemi başarıyla tamamlandı!")
