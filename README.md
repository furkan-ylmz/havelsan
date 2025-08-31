# AIS-Kamera Eşleştirme Sistemi

## Proje Amacı
Gemi üstü kameralardan gelen görüntülerdeki gemileri AIS verileriyle eşleştirmek.

## Dosyalar
- `main.py` - Ana menü sistemi
- `ais_matcher.py` - Core eşleştirme algoritması
- `simple_detector.py` - Video test sistemi

## Kurulum
```bash
pip install opencv-python numpy scipy
```

## Kullanım

### Ana menü:
```bash
python main.py
```

### Direkt test:
```bash
python ais_matcher.py
```

### Video testi:
```bash
python simple_detector.py
```

## Veri Formatı
Sistem **YOLO formatını** otomatik algılar:
- `yolo_data/` klasöründe JPG + TXT dosyaları
- Fallback: `test/` klasöründe LabelMe JSON formatı

YOLO format örneği:
```
0 0.724398 0.574645 0.035173 0.058021
0 0.634182 0.490921 0.008624 0.015633
```

## Nasıl Çalışır
1. Veriler YOLO formatından okunur
2. AIS pozisyonları kamera düzlemine projekte edilir  
3. Hungarian algoritması ile optimal eşleştirme yapılır
4. MMSI bazlı gemi takibi
