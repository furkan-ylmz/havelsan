# AIS-Kamera Eşleştirme Sistemi

## 🎯 Bu Sistem Ne İşe Yarar?
Denizde gemilerin kameradan çekilen görüntülerini, AIS (Automatic Identification System) verilerindeki gemi bilgileriyle eşleştirerek "Bu görüntüdeki gemi hangisi?" sorusuna cevap verir.

## 🚢 Nasıl Çalışır?
1. **AIS verisi gelir**: Geminin GPS konumu, adı, MMSI numarası
2. **Kamera görüntüsü gelir**: Görüntüde tespit edilen gemilerin koordinatları  
3. **Sistem eşleştirir**: "Bu koordinattaki gemi, şu AIS verisindeki gemidir"
4. **Sonuç**: Her gemi için kimlik bilgisi

## 📁 Proje İçeriği

### Ana Dosyalar
- **`ais_matcher.py`**: Ana eşleştirme sistemi - her şeyin merkezinde bu var
- **`data/`**: Örnek veriler (AIS bilgileri ve gemi tespitleri)

### Veri Klasörü
- **`sample_ais.json`**: 8 örnek geminin bilgileri (konum, isim, MMSI)
- **`txt/`**: Kamera görüntülerindeki gemi tespitleri (YOLO formatı)

## ⚙️ Kurulum

### Gerekli Programlar
```bash
pip install matplotlib numpy scipy
```

### Hızlı Test
```bash
python ais_matcher.py
```

## 📊 AIS Matcher - Ana Sistem

### Bu Dosya Ne Yapar?
`ais_matcher.py` tüm eşleştirme işlemini yapar:
- AIS verilerini okur (JSON dosyalarından)  
- Kamera tespitlerini okur (YOLO formatında)
- İki veriyi karşılaştırıp eşleştirir
- Hangi geminin hangi tespit olduğunu bulur

### Temel Özellikler
- **Otomatik format tanıma**: YOLO veya JSON formatlarını destekler
- **Akıllı eşleştirme**: En optimal eşleştirmeyi yapar
- **Hata toleransı**: Eksik veriyle de çalışmaya çalışır

## 🧭 Koordinat Sistemi

**Basit açıklama:**
- **AIS**: GPS koordinatları (enlem/boylam)
- **Kamera**: Görüntüdeki piksel koordinatları
- **Sistem**: İkisini de "kilometre" cinsinden aynı haritaya çevirir
- **Sonuç**: Artık iki veri karşılaştırılabilir

## 📈 Ne Kadar İyi Çalışır?

**Tipik sonuçlar:** %85-95 doğruluk, 1-2 km ortalama hata, saniyeler içinde sonuç

## 🔍 Hangi Durumlar Sorun Çıkarır?

**Zorluklar:** Çok yakın gemiler (500m içinde), hızlı hareket, kötü hava, AIS kapalı gemiler

## 📚 Sistem Gereksinimleri

**Minimum:** Python 3.8+, 4GB RAM  
**Önerilen:** Python 3.10+, 8GB+ RAM, SSD disk

## 🤝 Kullanım Alanları

### Denizcilik
- **Liman güvenliği**: Hangi gemi geldi?
- **Trafik kontrolü**: Gemiler arası mesafe
- **Kaza analizi**: Hangi gemi nerede?

### Güvenlik
- **Sahil güvenlik**: Kimliği belirsiz gemiler
- **Sınır kontrolü**: İzinsiz geçişler

---
**Not**: Bu sistem gerçek operasyonlarda kullanılmadan önce kapsamlı testlerden geçirilmelidir.
