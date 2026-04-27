from evds import evdsAPI
import requests
import pandas as pd
import os 
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import month_plot, quarter_plot
from dotenv import load_dotenv
load_dotenv('./.env')

""" 
# API anahtarınızı buraya yazın
API_KEY = os.getenv("EVDS_API_KEY")
evds = evdsAPI(API_KEY)

# 2. Ana kategorileri çek
df = evds.main_categories

search_term = input("Aramak istediğiniz kelimeleri girin: ").strip()

if search_term == "":
    print("Boş giriş yapıldı.")
else:
    # 1. Kullanıcının girdiği cümleyi kelimelere bölüyoruz
    # Örn: "piyasa verileri" -> ["piyasa", "verileri"]
    words = search_term.split()

    # 2. Her bir kelime için ayrı bir filtre oluşturup hepsini birleştiriyoruz
    # Bu 'AND' (VE) mantığıdır: word1 ve word2 ve word3 başlıkta geçmeli
    mask = True
    for word in words:
        mask &= df['TOPIC_TITLE_TR'].str.contains(word, case=False, na=False)

    filtered_df = df[mask]

    if not filtered_df.empty:
        # Sonuçları listele (Birden fazla sonuç çıkabilir, hepsini gösterelim)
        print(f"\n--- {len(filtered_df)} Sonuç Bulundu ---")
        print(filtered_df[['CATEGORY_ID', 'TOPIC_TITLE_TR']])
        
        # Eğer tek bir tane kalsın istiyorsan yine ilkini seçebilirsin
        hedef_id = filtered_df['CATEGORY_ID'].values[0]
    else:
        print(f"'{search_term}' içindeki kelimelerin tümünü içeren bir başlık bulunamadı.")

        



veri = evds.get_data(["TP.KTF12"], startdate="01-01-2010", enddate="01-04-2026")
print(veri.to_string())
veri = veri.dropna(subset=['Konut_Faizi'])
veri.columns = ['Tarih', 'Konut_Faizi']
veri.rename(columns={"TP.KTF12": "Konut_Faizi"}, inplace=True)
veri['Tarih'] = pd.to_datetime(veri['Tarih'])
veri['Konut_Faizi'] = pd.to_numeric(veri['Konut_Faizi'], errors='coerce')
print(veri.to_string())

# 5. Grafiği süsle
plt.figure(figsize=(12, 6))
plt.plot(veri['Tarih'], veri['Konut_Faizi'], color='red', linewidth=2, label='Konut Kredisi Faizi (%)')

plt.title("TCMB Verilerine Göre Konut Kredisi Faiz Trendi (2010-2026)", fontsize=14)
plt.xlabel("Zaman", fontsize=12)
plt.ylabel("Faiz (%)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

"""


# 1. BAĞLANTI
load_dotenv('./.env')
API_KEY = os.getenv("EVDS_API_KEY")
evds = evdsAPI(API_KEY)

# 2. VERİ ÇEKME
print("\n🚀 Veri çekiliyor: TP.KTF12...")
# Tarih aralığını geniş tutalım
veri = evds.get_data(["TP.KTF12"], startdate="01-01-2010", enddate="12-04-2026")

# 3. SÜTUN İSİMLERİNİ OTOMATİK AYARLA
# Sütun sayısına göre en sağdakini her zaman 'Konut_Faizi' yapalım
if len(veri.columns) == 3:
    veri.columns = ['Tarih', 'Gereksiz', 'Konut_Faizi']
else:
    veri.columns = ['Tarih', 'Konut_Faizi']

# 4. TARİH DÖNÜŞÜMÜ (Hatanın Çözümü Burada!)
# dayfirst=True diyerek '15-01'deki 15'in GÜN olduğunu zorla öğretiyoruz
veri['Tarih'] = pd.to_datetime(veri['Tarih'], dayfirst=True, errors='coerce')

# 5. SAYISAL DÖNÜŞÜM
veri['Konut_Faizi'] = pd.to_numeric(veri['Konut_Faizi'], errors='coerce')

# 6. TEMİZLİK (Hem geçersiz tarihleri hem geçersiz faizleri siler)
veri = veri.dropna(subset=['Tarih', 'Konut_Faizi'])

# Kontrol edelim (Ekrana bas)
print("\n✅ İşlenmiş Veri (Son 5 Satır):")
print(veri.to_string(index=False))

# 7. GRAFİK
if not veri.empty:
    plt.figure(figsize=(12, 6))
    plt.plot(veri['Tarih'], veri['Konut_Faizi'], color='red', linewidth=1.5)
    
    plt.title("Konut Kredisi Faiz Oranları Trendi (2010-2026)", fontsize=14)
    plt.xlabel("Yıl", fontsize=12)
    plt.ylabel("Faiz (%)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
else:
    print("❌ Hata: Çizilecek uygun veri kalmadı (Tüm veriler boş veya hatalı gelmiş olabilir).")
