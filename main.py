import instaloader
import os
import time

# Gizli kasadaki bilgileri alıyoruz
kullanici_adi = os.environ.get("IG_KULLANICI_ADI")
sifre = os.environ.get("IG_SIFRE")

L = instaloader.Instaloader()

print("Rakip analizi başlıyor...\n")

try:
    # Yeni hesabımızla giriş yapıyoruz
    L.login(kullanici_adi, sifre)
    print("Instagram'a giriş başarılı!\n")
except Exception as e:
    print(f"Giriş yapılamadı: {e}")
    exit()

with open("hesaplar.txt", "r") as dosya:
    hesaplar = dosya.read().splitlines()

for hesap in hesaplar:
    if hesap.strip(): 
        try:
            profil = instaloader.Profile.from_username(L.context, hesap.strip())
            print(f"{profil.username} sayfasının takipçi sayısı: {profil.followers}")
            # Engel yememek için her işlemden sonra 5 saniye bekletiyoruz
            time.sleep(5)
        except Exception as e:
            print(f"{hesap} sayfası bulunamadı veya bir hata oluştu.")

print("\nVeri çekme işlemi başarıyla tamamlandı!")
