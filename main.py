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

print("Rakip analizi ve Müzik Çalarlı Web Paneli hazırlığı başlıyor...\n")

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

sonuclar = sorted(sonuclar, key=lambda x: x['gercek_sayi'], reverse=True)

benim_sayim = "Bilinmiyor"
for s in sonuclar:
    if s['hesap'] == "turkishgeopoliticalmaps":
        benim_sayim = s['takipci_metin']
        break

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

satirlar_html = ""
sira = 1
for sonuc in sonuclar:
    satirlar_html += f"""                <tr class="tablo-satir" data-ulke="{sonuc['bayrak']}">
                    <td class="orta sira">{sira}</td>
                    <td>
                        <a class="link" href="https://instagram.com/{sonuc['hesap']}" target="_blank">@{sonuc['hesap']}</a>
                        <span class="bayrak">{sonuc['bayrak']}</span>
                    </td>
                    <td class="sag sayi">{sonuc['takipci_metin']}</td>
                    <td class="sag {sonuc['degisim_sinifi']}">{sonuc['degisim']}</td>
                </tr>\n"""
    sira += 1

grafik_data = {}
for h in gecmis_veriler:
    kayitlar = gecmis_veriler[h][-15:]
    grafik_data[h] = {
        "labels": [k["tarih"] for k in kayitlar],
        "data": [k["sayi"] for k in kayitlar]
    }

grafik_json = json.dumps(grafik_data, ensure_ascii=False)

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
            position: relative;
            min-height: 100vh;
        }
        
        body::before {
            content: "";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80vw;
            height: 80vh;
            max-width: 600px;
            background-image: url('logo.png');
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            opacity: 0.04;
            z-index: -1;
            pointer-events: none;
        }

        .profil-karti {
            position: fixed;
            top: 40px;
            left: 40px;
            background: rgba(22, 27, 34, 0.7);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            width: 220px;
            backdrop-filter: blur(8px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            z-index: 100;
            transition: transform 0.3s ease;
        }
        .profil-karti:hover {
            transform: translateY(-5px);
            border-color: #58a6ff;
        }
        .profil-logo {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #58a6ff;
            margin-bottom: 10px;
            background-color: #0d1117;
        }
        .profil-isim {
            color: #f0f6fc;
            font-size: 15px;
            font-weight: 600;
            margin: 5px 0;
            word-wrap: break-word;
        }
        .profil-istatistik {
            background: rgba(13, 17, 23, 0.8);
            border-radius: 6px;
            padding: 8px;
            margin-top: 15px;
            font-size: 13px;
            color: #8b949e;
            border: 1px solid #30363d;
        }
        .profil-istatistik span {
            display: block;
            font-size: 20px;
            font-weight: bold;
            color: #56d364;
            margin-top: 4px;
        }

        /* YENİ: Müzik Butonu Tasarımı */
        .muzik-btn {
            background: #238636;
            color: #ffffff;
            border: 1px solid rgba(240, 246, 252, 0.1);
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
            transition: background-color 0.2s;
        }
        .muzik-btn:hover {
            background: #2ea043;
        }
        .muzik-btn.aktif {
            background: #da3633;
        }
        .muzik-btn.aktif:hover {
            background: #f85149;
        }
        
        @media (max-width: 1300px) {
            body { flex-direction: column; align-items: center; }
            .profil-karti { position: relative; top: 0; left: 0; margin-bottom: 30px; width: 100%; max-width: 300px; }
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
        .ust-kisim {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }
        .guncelleme {
            color: #8b949e;
            font-size: 14px;
            background: rgba(22, 27, 34, 0.85);
            padding: 10px 15px;
            border-radius: 6px;
            border: 1px solid #30363d;
            backdrop-filter: blur(5px);
        }
        
        .filtre-kutusu {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filtre-kutusu label {
            color: #8b949e;
            font-size: 14px;
            font-weight: bold;
        }
        #bayrakFiltresi {
            background: #21262d;
            color: #f0f6fc;
            border: 1px solid #30363d;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            cursor: pointer;
            min-width: 150px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(22, 27, 34, 0.85);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #30363d;
            margin-bottom: 40px;
            backdrop-filter: blur(5px);
        }
        th, td { padding: 15px; text-align: left; }
        th { background-color: rgba(33, 38, 45, 0.9); color: #f0f6fc; font-weight: 600; border-bottom: 2px solid #30363d; }
        tr { border-bottom: 1px solid #30363d; }
        tr:last-child { border-bottom: none; }
        tr:hover { background-color: rgba(31, 36, 44, 0.95); }
        .sira { font-weight: bold; color: #8b949e; width: 50px; text-align: center; }
        .link { color: #58a6ff; text-decoration: none; font-weight: 500; }
        .link:hover { text-decoration: underline; }
        .bayrak { margin-left: 8px; display: inline-block; vertical-align: middle; }
        img.emoji { height: 1.2em; width: 1.2em; margin: 0 .05em 0 .1em; vertical-align: -0.1em; }
        .sayi { font-weight: 700; color: #f0f6fc; text-align: right; }
        .pozitif { color: #56d364; font-weight: 700; text-align: right; }
        .negatif { color: #f85149; font-weight: 700; text-align: right; }
        .notr { color: #8b949e; text-align: right; }
        th.sag, td.sag { text-align: right; }
        th.orta, td.orta { text-align: center; }
        .chart-box {
            background: rgba(22, 27, 34, 0.85);
            padding: 25px;
            border-radius: 8px;
            border: 1px solid #30363d;
            backdrop-filter: blur(5px);
        }
        .chart-box h2 { color: #58a6ff; font-size: 20px; margin-top: 0; margin-bottom: 15px; }
        #hesapSecici {
            background: #21262d; color: #f0f6fc; border: 1px solid #30363d;
            padding: 10px 15px; border-radius: 6px; font-size: 14px;
            margin-bottom: 25px; width: 100%; max-width: 320px;
            outline: none; cursor: pointer;
        }
    </style>
</head>
<body>

    <audio id="arkaMuzik" loop>
        <source src="muzik.mp3" type="audio/mpeg">
    </audio>

    <div class="profil-karti">
        <img src="logo.png" alt="TGM Logo" class="profil-logo">
        <div class="profil-isim">@turkishgeopoliticalmaps</div>
        <div class="profil-istatistik">
            Güncel Takipçi
            <span>[BENIM_SAYIM]</span>
        </div>
        <button id="muzikButonu" class="muzik-btn">🎵 Müziği Başlat</button>
    </div>

    <div class="container">
        <h1>📍 Harita Sayfaları Analiz Paneli</h1>
        
        <div class="ust-kisim">
            <div class="guncelleme">🔄 Son Güncelleme (TSİ): [SON_GUNCELLEME]</div>
            
            <div class="filtre-kutusu">
                <label for="bayrakFiltresi">Ülke Filtresi:</label>
                <select id="bayrakFiltresi" onchange="tabloyuFiltrele()">
                    <option value="hepsi">🌍 Tüm Ülkeler</option>
                </select>
            </div>
        </div>
        
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
        twemoji.parse(document.body);

        // Müzik Butonu İşlevi
        const sesDosyasi = document.getElementById("arkaMuzik");
        const sesButonu = document.getElementById("muzikButonu");

        sesButonu.addEventListener("click", function() {
            if (sesDosyasi.paused) {
                sesDosyasi.play();
                sesButonu.classList.add("aktif");
                sesButonu.innerHTML = "⏸️ Müziği Durdur";
            } else {
                sesDosyasi.pause();
                sesButonu.classList.remove("aktif");
                sesButonu.innerHTML = "🎵 Müziği Başlat";
            }
        });

        const tabloSatirlari = document.querySelectorAll(".tablo-satir");
        const bayrakSeti = new Set();
        
        tabloSatirlari.forEach(satir => {
            const bayrak = satir.getAttribute("data-ulke").trim();
            if(bayrak !== "") {
                bayrakSeti.add(bayrak);
            }
        });

        const filtreSelect = document.getElementById("bayrakFiltresi");
        bayrakSeti.forEach(bayrak => {
            const opt = document.createElement("option");
            opt.value = bayrak;
            opt.innerText = bayrak + " Ülkesi";
            filtreSelect.appendChild(opt);
        });
        
        twemoji.parse(filtreSelect);

        function tabloyuFiltrele() {
            const secilen = filtreSelect.value;
            let siraSayaci = 1;
            
            tabloSatirlari.forEach(satir => {
                const bayrak = satir.getAttribute("data-ulke").trim();

                if(secilen === "hepsi" || bayrak === secilen) {
                    satir.style.display = ""; 
                    satir.querySelector(".sira").innerText = siraSayaci;
                    siraSayaci++;
                } else {
                    satir.style.display = "none"; 
                }
            });
        }

        const grafikVerisi = [GRAFIK_JSON];
        const select = document.getElementById('hesapSecici');
        
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
            if (myChart) myChart.destroy();
            
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
                        x: { grid: { color: '#30363d' }, ticks: { color: '#8b949e' } },
                        y: { grid: { color: '#30363d' }, ticks: { color: '#8b949e' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }
        
        if (select.value) grafikCiz(select.value);
        select.addEventListener('change', (e) => grafikCiz(e.target.value));
    </script>
</body>
</html>"""

html_icerik = html_taslak.replace("[SON_GUNCELLEME]", tarih_formatli)
html_icerik = html_icerik.replace("[TABLO_SATIRLARI]", satirlar_html)
html_icerik = html_icerik.replace("[GRAFIK_JSON]", grafik_json)
html_icerik = html_icerik.replace("[BENIM_SAYIM]", benim_sayim)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)

print("\nGelişmiş web paneli müzik çalarla birlikte başarıyla üretildi!")
