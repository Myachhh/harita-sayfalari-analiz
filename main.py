import requests
import os
import time
import re
import json
from datetime import datetime, timedelta

session_id = os.environ.get("IG_SESSIONID")

cookies = {'sessionid': session_id}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

print("Rakip analizi ve Gelişmiş Grafik Paneli hazırlığı behaviör...\n")

tarih_formatli = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y - %H:%M")
tarih_kisa = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y")

def sayiya_cevir(metin):
    m = metin.upper().replace(',', '')
    try:
        if 'K' in m: return int(float(m.replace('K', '')) * 1000)
        if 'M' in m: return int(float(m.replace('M', '')) * 1000000)
        return int(m)
    except:
        return 0

# 1. ADIM: ÖNCEKİ GÜNCELLEMELERİ VE GEÇMİŞİ OKUYORUZ
gecmis_veriler = {}
if os.path.exists("takipciler.csv"):
    with open("takipciler.csv", "r", encoding="utf-8") as f:
        for line in f:
            parcalar = line.strip().split(",")
            if len(parcalar) >= 3:
                h_tarih = parcalar[0]
                h_hesap = parcalar[1]
                h_metin = ",".join(parcalar[2:])
                
                h_tarih_kisa = h_tarih.split("-")[0].strip()
                if h_hesap not in gecmis_veriler:
                    gecmis_veriler[h_hesap] = []
                gecmis_veriler[h_hesap].append({
                    "tarih": h_tarih_kisa,
                    "sayi": sayiya_cevir(h_metin),
                    "metin": h_metin
                })

sonuclar = []
dosya_kayit = open("takipciler.csv", "a", encoding="utf-8")

with open("hesaplar.txt", "r", encoding="utf-8") as dosya:
    hesaplar = dosya.read().splitlines()

for satir in hesaplar:
    satir = satir.strip()
    if satir:
        if "," in satir:
            parcalar = satir.split(",")
            hesap = parcalar[0].strip()
            bayrak = parcalar[1].strip()
        else:
            hesap = satir
            bayrak = ""
            
        if hesap: 
            try:
                url = f"https://www.instagram.com/{hesap}/"
                response = requests.get(url, cookies=cookies, headers=headers)
                match = re.search(r'content="([^"]+?)\s+Followers', response.text)
                
                if match:
                    takipci_metin = match.group(1)
                    gercek_sayi = sayiya_cevir(takipci_metin)
                    
                    # 2. ADIM: BİR ÖNCEKİ VERİYE GÖRE DEĞİŞİM HESAPLAMA
                    degisim_metni = ""
                    degisim_sinifi = "notr"
                    if hesap in gecmis_veriler and len(gecmis_veriler[hesap]) > 0:
                        son_kayit = gecmis_veriler[hesap][-1]
                        eski_sayi = son_kayit["sayi"]
                        fark = gercek_sayi - eski_sayi
                        if fark > 0:
                            degisim_metni = f"+{fark}"
                            degisim_sinifi = "pozitif"
                        elif fark < 0:
                            degisim_metni = f"{fark}"
                            degisim_sinifi = "negatif"
                        else:
                            degisim_metni = "0"
                            degisim_sinifi = "notr"
                    else:
                        degisim_metni = "Yeni"
                        degisim_sinifi = "pozitif"
                    
                    print(f"{hesap} {bayrak}: {takipci_metin} ({degisim_metni})")
                    dosya_kayit.write(f"{tarih_formatli},{hesap},{takipci_metin}\n")
                    
                    sonuclar.append({
                        "hesap": hesap,
                        "bayrak": bayrak,
                        "takipci_metin": takipci_metin,
                        "gercek_sayi": gercek_sayi,
                        "degisim": degisim_metni,
                        "degisim_sinifi": degisim_sinifi
                    })
                    
                    # Grafik verisine bugünün taze kaydını da ekleyelim
                    if hesap not in gecmis_veriler:
                        gecmis_veriler[hesap] = []
                    gecmis_veriler[hesap].append({
                        "tarih": tarih_kisa,
                        "sayi": gercek_sayi,
                        "metin": takipci_metin
                    })
                else:
                    print(f"{hesap} okunamadı.")
                time.sleep(5)
            except Exception as e:
                print(f"Hata: {e}")

dosya_kayit.close()

# Takipçiye göre büyükten küçüğe sıralama
sonuclar = sorted(sonuclar, key=lambda x: x['gercek_sayi'], reverse=True)

# 3. ADIM: README.MD (VİTRİN) GÜNCELLEME
readme_icerik = "# Harita Sayfaları Analiz Paneli\n\n"
readme_icerik += f"**Son Güncelleme:** {tarih_formatli}\n\n"
readme_icerik += "| Sıra | Sayfa Adı | Takipçi Sayısı | Değişim |\n"
readme_icerik += "| :---: | :--- | :---: | :---: |\n"
sira = 1
for sonuc in sonuclar:
    isim_gosterim = f"@{sonuc['hesap']} {sonuc['bayrak']}".strip()
    readme_icerik += f"| {sira} | [{isim_gosterim}](https://instagram.com/{sonuc['hesap']}) | **{sonuc['takipci_metin']}** | {sonuc['degisim']} |\n"
    sira += 1
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_icerik)

# 4. ADIM: DİNAMİK WEB TABLOSU SATIRLARINI ÜRETME
satirlar_html = ""
sira = 1
for sonuc in sonuclar:
    satirlar_html += f"""                <tr>
                    <td class="orta sira">{sira}</td>
                    <td>
                        <a class="link" href="https://instagram.com/{sonuc['hesap']}" target="_blank">@{sonuc['hesap']}</a>
                        <span class="bayrak">{sonuc['bayrak']}</span>
                    </td>
                    <td class="sag sayi">{sonuc['takipci_metin']}</td>
                    <td class="sag {sonuc['degisim_sinifi']}">{sonuc['degisim']}</td>
                </tr>\n"""
    sira += 1

# 5. ADIM: GRAFİK İÇİN GEÇMİŞ VERİLERİ JS FORMATINA ÇEVİRME
grafik_data = {}
for h in gecmis_veriler:
    # Grafiğin çok şişmemesi için son 15 güncellemeyi alıyoruz
    kayitlar = gecmis_veriler[h][-15:]
    grafik_data[h] = {
        "labels": [k["tarih"] for k in kayitlar],
        "data": [k["sayi"] for k in kayitlar]
    }

grafik_json = json.dumps(grafik_data, ensure_ascii=False)

# 6. ADIM: HTML ŞABLONUNU HAZIRLAMA VE YAZMA
html_taslak = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harita Sayfaları Analiz Paneli</title>
    <script src="https://cdn.jsdelivr.net/npm/@twemoji/api@14.1.0/dist/twemoji.min.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 850px;
        }
        h1 {
            color: #58a6ff;
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .guncelleme {
            color: #8b949e;
            font-size: 14px;
            margin-bottom: 30px;
            background: #161b22;
            padding: 10px 15px;
            border-radius: 6px;
            display: inline-block;
            border: 1px solid #30363d;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #161b22;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #30363d;
            margin-bottom: 40px;
        }
        th, td {
            padding: 15px;
            text-align: left;
        }
        th {
            background-color: #21262d;
            color: #f0f6fc;
            font-weight: 600;
            border-bottom: 2px solid #30363d;
        }
        tr {
            border-bottom: 1px solid #30363d;
        }
        tr:last-child {
            border-bottom: none;
        }
        tr:hover {
            background-color: #1f242c;
        }
        .sira {
            font-weight: bold;
            color: #8b949e;
            width: 50px;
            text-align: center;
        }
        .link {
            color: #58a6ff;
            text-decoration: none;
            font-weight: 500;
        }
        .link:hover {
            text-decoration: underline;
        }
        .bayrak {
            margin-left: 8px;
            display: inline-block;
            vertical-align: middle;
        }
        img.emoji {
            height: 1.2em;
            width: 1.2em;
            margin: 0 .05em 0 .1em;
            vertical-align: -0.1em;
        }
        .sayi {
            font-weight: 700;
            color: #f0f6fc;
            text-align: right;
        }
        .pozitif { color: #56d364; font-weight: 700; text-align: right; }
        .negatif { color: #f85149; font-weight: 700; text-align: right; }
        .notr { color: #8b949e; text-align: right; }
        th.sag, td.sag {
            text-align: right;
        }
        th.orta, td.orta {
            text-align: center;
        }
        .chart-box {
            background: #161b22;
            padding: 25px;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        .chart-box h2 {
            color: #58a6ff;
            font-size: 20px;
            margin-top: 0;
            margin-bottom: 15px;
        }
        select {
            background: #21262d;
            color: #f0f6fc;
            border: 1px solid #30363d;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 25px;
            width: 100%;
            max-width: 320px;
            outline: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 Harita Sayfaları Analiz Paneli</h1>
        <div class="guncelleme">🔄 Son Güncelleme (TSİ): [SON_GUNCELLEME]</div>
        
        <table>
            <thead>
                <tr>
                    <th class="orta">Sıra</th>
                    <th>Sayfa Adı</th>
                    <th class="sag">Takipçi Sayısı</th>
                    <th class="sag">Değişim</th>
                </tr>
            </thead>
            <tbody>
[TABLO_SATIRLARI]
            </tbody>
        </table>

        <div class="chart-box">
            <h2>📈 Sayfa Gelişim Grafiği</h2>
            <select id="hesapSecici">
                </select>
            <canvas id="gelişimGrafigi"></canvas>
        </div>
    </div>

    <script>
        // PC'deki emojileri yakalayıp resim yapan sihirli kod
        twemoji.parse(document.body);

        const grafikVerisi = [GRAFIK_JSON];
        const select = document.getElementById('hesapSecici');
        
        // Dropdown menüyü dolduruyoruz
        Object.keys(grafikVerisi).forEach(hesap => {
            const opt = document.createElement('option');
            opt.value = hesap;
            opt.innerHTML = '@' + hesap;
            select.appendChild(opt);
        });
        
        const ctx = document.getElementById('gelişimGrafigi').getContext('2d');
        let myChart;
        
        function grafikCiz(hesap) {
            const veri = grafikVerisi[hesap];
            if (!veri) return;
            
            if (myChart) {
                myChart.destroy();
            }
            
            myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: veri.labels,
                    datasets: [{
                        label: 'Takipçi Sayısı',
                        data: veri.data,
                        borderColor: '#58a6ff',
                        backgroundColor: 'rgba(88, 166, 255, 0.05)',
                        borderWidth: 2,
                        tension: 0.2,
                        fill: true,
                        pointBackgroundColor: '#58a6ff'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            grid: { color: '#30363d' },
                            ticks: { color: '#8b949e' }
                        },
                        y: {
                            grid: { color: '#30363d' },
                            ticks: { color: '#8b949e' }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
        
        // İlk açılışta ilk hesabı çiz
        if (select.value) {
            grafikCiz(select.value);
        }
        
        // Hesap değiştikçe grafiği güncelle
        select.addEventListener('change', (e) => {
            grafikCiz(e.target.value);
        });
    </script>
</body>
</html>"""

html_icerik = html_taslak.replace("[SON_GUNCELLEME]", tarih_formatli)
html_icerik = html_icerik.replace("[TABLO_SATIRLARI]", satirlar_html)
html_icerik = html_icerik.replace("[GRAFIK_JSON]", grafik_json)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)

print("\nGelişmiş web paneli grafiklerle birlikte başarıyla üretildi!")
