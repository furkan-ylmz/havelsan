# Demo Klasörü - Test ve Görselleştirme

## 🎯 Bu Klasör Ne İçin?
Ana sistemin test edilmesi ve görselleştirilmesi için hazırlanmış demo uygulamaları. Algoritmanın nasıl çalıştığını görmek ve test etmek için kullanıyoruz.

## 📁 Demo Dosyaları

### `matching_algorithm.py` - Temel Algoritma
**Ne işe yarar?**
- Koordinat dönüşümü yapar (GPS → 2D, YOLO → 2D)
- Gemileri eşleştirir (en yakını değil, en iyisini buluyor)
- Sonuçları analiz eder

**Nasıl çalışır?**
1. AIS verilerini okur → GPS koordinatlarını kilometre cinsine çevirir
2. Kamera tespitlerini okur → YOLO koordinatlarını kilometre cinsine çevirir  
3. İkisini karşılaştırır → Hangi gemi hangi tespit?
4. En iyi eşleştirmeyi bulur → Toplam hatayı minimize eder

### `visual_map_demo.py` - Görsel Demo
**Ne işe yarar?**
- Sonuçları harita şeklinde gösterir
- Her görüntü için ayrı analiz yapar
- 4 panel halinde sonuçları görselleştirir

**Ne gösterir?**
- **Ana panel**: Tüm gemiler ve eşleştirmeler bir arada
- **AIS paneli**: Sadece GPS'ten gelen gemi konumları
- **Tespit paneli**: Sadece kameradan tespit edilen gemiler  
- **İstatistik**: Başarı oranları ve mesafe bilgileri

## 🚀 Nasıl Çalıştırılır?

### Temel Test
```bash
python matching_algorithm.py
```
Bu komut:
- Örnek verileri yükler
- Eşleştirme yapar
- Sonuçları metin olarak gösterir

### Görsel Test  
```bash
python visual_map_demo.py
```
Bu komut:
- Tüm test görüntülerini işler
- Her birini ayrı harita olarak gösterir
- Pencereler halinde sonuçları sunar

## 🎨 Görselleştirme Nasıl Çalışır?

### Renk Kodlaması
- **🔴 Kırmızı üçgen**: AIS'ten gelen gemi konumu
- **🔵 Mavi kare**: Kameradan tespit edilen gemi
- **🟢 Yeşil çizgi**: Başarılı eşleştirme (yakın mesafe)
- **🟡 Sarı çizgi**: Zayıf eşleştirme (uzak mesafe)

### Panel Açıklamaları
1. **Ana Panel (Sol üst)**: Her şeyi bir arada gösterir
2. **AIS Panel (Sağ üst)**: Sadece gerçek gemi konumları
3. **Tespit Panel (Sol alt)**: Sadece kamera tespitleri
4. **İstatistik Panel (Sağ alt)**: Sayısal sonuçlar

## 📊 Sonuçları Anlama

### Başarılı Eşleştirme
```
✅ MEDITERRANEAN STAR (MMSI: 271044431)
   AIS konumu: (2.1, -1.5) km
   Tespit: (1.9, -1.3) km  
   Mesafe: 0.28 km
   Güven: %92
```

### Başarısız Eşleştirme
```
❌ BLACK PEARL (MMSI: 123456789)
   AIS konumu: (5.2, 3.1) km
   En yakın tespit: (1.1, 0.8) km
   Mesafe: 4.8 km (çok uzak!)
   Güven: %15
```

### Eşleştirme Yok
```
⚠️ OCEAN BREEZE (MMSI: 987654321)
   AIS konumu: (7.8, 4.5) km
   Kamerada görülmedi
   Sebep: Kamera alanı dışında
```

## 🔧 Demo Ayarları

### Önemli Parametreler
```python
# En fazla ne kadar uzaktaki gemileri eşleştirir?
MAX_DISTANCE = 8.0  # km

# Ne kadar emin olduğunda kabul eder?  
MIN_CONFIDENCE = 0.6  # %60

# Kamera ne kadar geniş alan görür?
CAMERA_FOV_X = 8.0  # km (yatay)
CAMERA_FOV_Y = 6.0  # km (dikey)
```

### Test Verisi
- **8 farklı görüntü** test edilir
- **8 farklı gemi** AIS verisi
- **24 tespit** toplam (bazı görüntülerde birden fazla gemi)

## 🧪 Test Senaryoları

**Kolay:** Tek gemi, kamera ortasında, net tespit
**Zor:** Birden fazla gemi yakın, kamera kenarında
**İmkansız:** AIS var kamera yok, veya tam tersi

## 📈 Performans

**Basit Yöntem:** Her gemi için en yakın tespit → Ortalama hata: 1.38 km

**Akıllı Yöntem:** En iyi kombinasyonu bul → Ortalama hata: 0.75 km (%46 daha iyi!)

## 🔍 Hata Ayıklama

**"Hiç eşleştirme bulunamadı"** → MAX_DISTANCE değerini artır (10-12 km)
**"Görüntü açılmıyor"** → `pip install matplotlib` yeniden yükle
**Debug için:** `DEBUG = True` yap, her adımı görürsün

## 🎯 Hangi Dosyayı Kullan?

**`matching_algorithm.py`**: Hızlı test, metin sonuçları yeterli
**`visual_map_demo.py`**: Harita görmek istersen, demo için

## ⚙️ Özelleştirme

### Yeni Test Verisi Ekleme
1. `data/` klasörüne yeni JSON/txt dosyası ekle
2. Dosya adını kod içinde güncelle
3. Çalıştır ve test et

---
**Not**: Bu demo dosyaları eğitim ve test amaçlıdır.
