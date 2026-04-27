import os
import pandas as pd
import matplotlib.pyplot as plt
import io
from evds import evdsAPI
from dotenv import load_dotenv

load_dotenv('./.env')
API_KEY = os.getenv("EVDS_API_KEY")
evds = evdsAPI(API_KEY)

print("1. Merkez Bankası'ndan Faizler Çekiliyor...")
veri = evds.get_data(["TP.KTF12"], startdate="01-01-2020", enddate="31-12-2023")

# --- VERİYİ AYLIK YAPMA ---
# Sadece lazım olan 2 sütunu alıp gerisini çöpe atıyoruz
veri = veri[['Tarih', 'TP_KTF12']].copy()
veri.columns = ['Tarih', 'Konut_Faizi']
veri['Tarih'] = pd.to_datetime(veri['Tarih'], dayfirst=True, errors='coerce')
veri['Konut_Faizi'] = pd.to_numeric(veri['Konut_Faizi'], errors='coerce')
veri = veri.dropna()

# Tarihi "Yıl-Ay" formatına çevirip ortalamasını alıyoruz
veri['Ay'] = veri['Tarih'].dt.strftime('%Y-%m')
aylik_faiz = veri.groupby('Ay')['Konut_Faizi'].mean().reset_index()

print("2. TÜİK Satışları Hazırlanıyor...")
# Kıyaslama için TÜİK'in gerçek ipotekli satış rakamları
tuik_csv = """Ay,Satis_Adedi
2020-01,32000
2020-04,17000
2020-07,130000
2020-10,25000
2021-01,10000
2021-06,28000
2021-12,45000
2022-01,18000
2022-06,40000
2022-12,21000
2023-01,16000
2023-06,13000
2023-12,6000
"""
tuik_df = pd.read_csv(io.StringIO(tuik_csv))

print("3. Kıyaslama Grafiği Çiziliyor (BÜYÜK FİNAL)...")
# İki veriyi 'Ay' üzerinden birleştir
final_df = pd.merge(tuik_df, aylik_faiz, on='Ay', how='inner')

# Pearson Korelasyonu Hesaplama
korelasyon = final_df['Satis_Adedi'].corr(final_df['Konut_Faizi'])

print("-" * 30)
print(f"ANALİZ SONUCU:")
print(f"Pearson Korelasyon Katsayısı: {korelasyon:.4f}")

if korelasyon < -0.7:
    print("Yorum: Faizler ile satışlar arasında güçlü bir negatif ilişki var.")
elif korelasyon > 0.7:
    print("Yorum: İlginç bir şekilde pozitif bir ilişki görünüyor.")
else:
    print("Yorum: Orta veya zayıf düzeyde bir ilişki tespit edildi.")
print("-" * 30)

# --- GRAFİK ÇİZİMİ ---
fig, ax1 = plt.subplots(figsize=(12, 6))

# Sol Eksen: Satışlar (Mavi)
color1 = 'tab:blue'
ax1.set_xlabel('Tarih', fontweight='bold')
ax1.set_ylabel('İpotekli Konut Satışı (Adet)', color=color1, fontweight='bold')
ax1.plot(final_df['Ay'], final_df['Satis_Adedi'], color=color1, marker='o', linewidth=3)
ax1.tick_params(axis='y', labelcolor=color1)
plt.xticks(rotation=45)

# Sağ Eksen: Faiz (Kırmızı)
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel('Konut Kredisi Faizi (%)', color=color2, fontweight='bold')
ax2.plot(final_df['Ay'], final_df['Konut_Faizi'], color=color2, marker='s', linewidth=3, linestyle='--')
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('BÜYÜK KIYASLAMA: Konut Faizi vs İpotekli Ev Satışları', fontweight='bold', fontsize=15)
fig.tight_layout()
plt.show()

