import instaloader

# Instagram'a bağlanacak robotumuzu hazırlıyoruz
L = instaloader.Instaloader()

print("Rakip analizi başlıyor...\n")

# hesaplar.txt dosyasındaki isimleri okuyoruz
with open("hesaplar.txt", "r") as dosya:
    hesaplar = dosya.read().splitlines()

# Listedeki her bir hesap için sırayla işlem yapıyoruz
for hesap in hesaplar:
    if hesap.strip():  # Eğer listede yanlışlıkla boş satır bıraktıysak onu atlıyor
        try:
            # Profil bilgilerini çekiyoruz
            profil = instaloader.Profile.from_username(L.context, hesap.strip())
            print(f"{profil.username} sayfasının takipçi sayısı: {profil.followers}")
        except Exception as e:
            print(f"{hesap} sayfası bulunamadı veya bir hata oluştu.")

print("\nVeri çekme işlemi başarıyla tamamlandı!")
