import instaloader
import os
import time

# Gizli kasadan VIP kartımızı (Session ID) alıyoruz
session_id = os.environ.get("IG_SESSIONID")

L = instaloader.Instaloader()

print("Rakip analizi başlıyor...\n")

try:
    # Instagram'a şifreyle değil, VIP kartla (Çerez) giriyoruz
    L.context._session.cookies.set('sessionid', session_id, domain='.instagram.com')
    print("Çerez (Cookie) ile bağlantı başarıyla kuruldu!\n")
except Exception as e:
    print(f"Bağlantı hatası: {e}")
    exit()

with open("hesaplar.txt", "r") as dosya:
    hesaplar = dosya.read().splitlines()

for hesap in hesaplar:
    if hesap.strip(): 
        try:
            profil = instaloader.Profile.from_username(L.context, hesap.strip())
            print(f"{profil.username} sayfasının takipçi sayısı: {profil.followers}")
            time.sleep(5)
        except Exception as e:
            print(f"{hesap} sayfası bulunamadı veya bir hata oluştu: {e}")

print("\nVeri çekme işlemi başarıyla tamamlandı!")
