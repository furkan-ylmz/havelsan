"""
Görsel Harita Demo
=================
Matplotlib ile gerçek harita görselleştirme
"""

import json
import math
from pathlib import Path
import os

# Matplotlib backend'ini ayarla
import matplotlib
matplotlib.use('TkAgg')  # Veya 'Qt5Agg' dene
import matplotlib.pyplot as plt
import numpy as np

# Türkçe font desteği için
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False

def load_ais_data(json_path):
    """AIS verilerini yükle"""
    points = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reference_lat, reference_lon = 40.0, 32.0
        
        for vessel in data.get('sample_vessels', []):
            lat = vessel.get('lat', 0.0)
            lon = vessel.get('lon', 0.0)
            
            # Koordinat dönüşümü
            x = (lon - reference_lon) * 111000 * math.cos(math.radians(reference_lat)) / 1000
            y = (lat - reference_lat) * 111000 / 1000
            
            point = {
                'x': x, 'y': y,
                'mmsi': vessel.get('mmsi', 0),
                'name': vessel.get('ship_name', ''),
                'lat': lat, 'lon': lon
            }
            points.append(point)
        
        return points
        
    except Exception as e:
        print(f"❌ AIS verisi yüklenirken hata: {e}")
        return []

def calibrate_coordinate_transformation(ais_points, detection_points):
    """
    AIS ve tespit koordinatları arasındaki ölçeklendirme faktörlerini hesapla
    """
    if len(ais_points) < 2 or len(detection_points) < 2:
        # Yeterli nokta yoksa varsayılan değerleri kullan
        return 20.0, 15.0
    
    # AIS noktalarının aralığını hesapla
    ais_x_values = [p['x'] for p in ais_points]
    ais_y_values = [p['y'] for p in ais_points]
    ais_x_range = max(ais_x_values) - min(ais_x_values)
    ais_y_range = max(ais_y_values) - min(ais_y_values)
    
    # Tespit noktalarının normalize aralığını hesapla
    det_x_values = [p['norm_x'] for p in detection_points]
    det_y_values = [p['norm_y'] for p in detection_points] 
    det_x_range = max(det_x_values) - min(det_x_values)
    det_y_range = max(det_y_values) - min(det_y_values)
    
    # Ölçeklendirme faktörlerini hesapla
    if det_x_range > 0:
        scale_x = ais_x_range / det_x_range
    else:
        scale_x = 20.0
        
    if det_y_range > 0:
        scale_y = ais_y_range / det_y_range
    else:
        scale_y = 15.0
    
    print(f"  Hesaplanan ölçek: X={scale_x:.2f}, Y={scale_y:.2f}")
    return scale_x, scale_y

def load_detection_data_per_image(data_dir, image_name):
    """Belirli bir görüntü için tespit verilerini yükle"""
    points = []
    
    txt_path = Path(data_dir) / "txt" / f"{image_name}.txt"
    
    if not txt_path.exists():
        return points
    
    try:
        with open(txt_path, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) != 5:
                    continue
                
                _, center_x, center_y, width, height = map(float, parts)
                
                # İlk olarak normalize koordinatları kaydet
                point = {
                    'image': image_name,
                    'id': line_num + 1,
                    'norm_x': center_x,
                    'norm_y': center_y,
                    'width': width,
                    'height': height,
                    'x': 0.0,  # Daha sonra kalibre edilecek
                    'y': 0.0   # Daha sonra kalibre edilecek
                }
                points.append(point)
                
    except Exception as e:
        print(f"Hata {txt_path}: {e}")
    
    return points

def apply_coordinate_transformation(detection_points, scale_x=None, scale_y=None):
    """Tespit noktalarına kalibre edilmiş koordinat dönüşümü uygula"""
    # Makul sabit ölçeklendirme kullan (kamera görüş alanı için)
    if scale_x is None:
        scale_x = 8.0  # ~8 km genişlik
    if scale_y is None:
        scale_y = 6.0  # ~6 km yükseklik
        
    for point in detection_points:
        # Daha makul ölçeklendirme ile koordinat dönüşümü
        point['x'] = (point['norm_x'] - 0.5) * scale_x
        point['y'] = (0.5 - point['norm_y']) * scale_y

def get_available_images(data_dir):
    """Mevcut görüntü isimlerini getir"""
    txt_path = Path(data_dir) / "txt"
    
    if not txt_path.exists():
        return []
    
    txt_files = list(txt_path.glob("*.txt"))
    return [txt_file.stem for txt_file in txt_files]

def load_detection_data(data_dir):
    """Tespit verilerini yükle (eski versiyon - geriye uyumluluk için)"""
    points = []
    
    txt_path = Path(data_dir) / "txt"
    
    if not txt_path.exists():
        return points
    
    txt_files = list(txt_path.glob("*.txt"))
    
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r') as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        continue
                    
                    _, center_x, center_y, width, height = map(float, parts)
                    
                    # Koordinat dönüşümü
                    x = (center_x - 0.5) * 20
                    y = (0.5 - center_y) * 15
                    
                    point = {
                        'x': x, 'y': y,
                        'image': txt_file.stem,
                        'id': line_num + 1,
                        'norm_x': center_x,
                        'norm_y': center_y,
                        'width': width,
                        'height': height
                    }
                    points.append(point)
                    
        except Exception as e:
            print(f"Hata {txt_file}: {e}")
    
    return points

def calculate_matching(ais_points, detection_points, max_distance=8.0):
    """Hungarian algoritması ile optimal eşleştirme"""
    if not ais_points or not detection_points:
        return []
    
    # Maliyet matrisi oluştur
    n_ais = len(ais_points)
    n_det = len(detection_points)
    
    # Sadece Python kullanarak Hungarian algoritması
    cost_matrix = []
    
    for i, ais in enumerate(ais_points):
        row = []
        for j, det in enumerate(detection_points):
            distance = math.sqrt((ais['x'] - det['x'])**2 + (ais['y'] - det['y'])**2)
            if distance <= max_distance:
                row.append(distance)
            else:
                row.append(999.0)  # Çok yüksek maliyet (eşleştirme yok)
        cost_matrix.append(row)
    
    # Basit greedy optimal eşleştirme (Hungarian'a yakın)
    matches = []
    used_detections = set()
    
    # Tüm olası eşleştirmeleri hesapla ve en iyi kombinasyonu bul
    possible_pairs = []
    
    for i, ais in enumerate(ais_points):
        for j, det in enumerate(detection_points):
            distance = cost_matrix[i][j]
            if distance < 999.0:
                possible_pairs.append({
                    'ais_idx': i,
                    'det_idx': j,
                    'ais': ais,
                    'detection': det,
                    'distance': distance
                })
    
    # Mesafeye göre sırala
    possible_pairs.sort(key=lambda x: x['distance'])
    
    # Greedy optimal seçim
    used_ais = set()
    used_det = set()
    
    for pair in possible_pairs:
        if pair['ais_idx'] not in used_ais and pair['det_idx'] not in used_det:
            confidence = max(0, 1 - pair['distance'] / max_distance)
            matches.append({
                'ais': pair['ais'],
                'detection': pair['detection'],
                'distance': pair['distance'],
                'confidence': confidence
            })
            used_ais.add(pair['ais_idx'])
            used_det.add(pair['det_idx'])
    
    return matches

def create_visual_map(ais_points, detection_points, matches):
    """Görsel harita oluştur"""
    
    # Figure boyutunu ayarla
    plt.figure(figsize=(16, 12))
    
    # Ana harita (2x2 grid'in üst yarısı)
    ax_main = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    
    # AIS haritası (alt sol)
    ax_ais = plt.subplot2grid((2, 2), (1, 0))
    
    # Tespit haritası (alt sağ)
    ax_det = plt.subplot2grid((2, 2), (1, 1))
    
    # Ana harita - Birleşik görünüm
    ax_main.set_title('🗺️ AIS-Kamera Eşleştirme Haritası', fontsize=16, fontweight='bold', pad=20)
    ax_main.grid(True, alpha=0.3, linestyle='--')
    ax_main.set_xlabel('X Koordinatı (km)', fontsize=12)
    ax_main.set_ylabel('Y Koordinatı (km)', fontsize=12)
    
    # AIS noktaları - Ana harita
    if ais_points:
        ais_x = [p['x'] for p in ais_points]
        ais_y = [p['y'] for p in ais_points]
        
        scatter_ais = ax_main.scatter(ais_x, ais_y, 
                                     c='red', s=200, alpha=0.8, 
                                     marker='o', edgecolors='darkred', 
                                     linewidth=2, label=f'AIS Noktaları ({len(ais_points)})')
        
        # AIS etiketleri
        for point in ais_points:
            ax_main.annotate(f"{point['name'][:12]}\nMMSI:{point['mmsi']}", 
                           (point['x'], point['y']), 
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor="red", alpha=0.7, 
                                   edgecolor='darkred'))
    
    # Tespit noktaları - Ana harita
    if detection_points:
        det_x = [p['x'] for p in detection_points]
        det_y = [p['y'] for p in detection_points]
        
        scatter_det = ax_main.scatter(det_x, det_y, 
                                     c='blue', s=150, alpha=0.7, 
                                     marker='^', edgecolors='darkblue', 
                                     linewidth=2, label=f'Tespit Noktaları ({len(detection_points)})')
        
        # Tespit etiketleri (sadece ilk 10 tanesini göster)
        for i, point in enumerate(detection_points[:10]):
            ax_main.annotate(f"T{i+1}", 
                           (point['x'], point['y']), 
                           xytext=(5, -15), textcoords='offset points',
                           fontsize=8,
                           bbox=dict(boxstyle="round,pad=0.2", 
                                   facecolor="blue", alpha=0.6))
    
    # Eşleştirme çizgileri - Ana harita
    if matches:
        for i, match in enumerate(matches):
            # Çizgi rengi güvene göre
            if match['confidence'] > 0.8:
                line_color = 'green'
                line_width = 3
                alpha = 0.9
            elif match['confidence'] > 0.6:
                line_color = 'orange'
                line_width = 2
                alpha = 0.8
            else:
                line_color = 'red'
                line_width = 1
                alpha = 0.7
            
            ax_main.plot([match['ais']['x'], match['detection']['x']], 
                        [match['ais']['y'], match['detection']['y']], 
                        color=line_color, linewidth=line_width, alpha=alpha)
            
            # Mesafe etiketi
            mid_x = (match['ais']['x'] + match['detection']['x']) / 2
            mid_y = (match['ais']['y'] + match['detection']['y']) / 2
            
            ax_main.annotate(f"D:{match['distance']:.1f}\nG:{match['confidence']:.2f}", 
                           (mid_x, mid_y), 
                           fontsize=8, ha='center',
                           bbox=dict(boxstyle="round,pad=0.2", 
                                   facecolor=line_color, alpha=0.8))
    
    ax_main.legend(loc='upper right', fontsize=12)
    ax_main.set_aspect('equal', adjustable='box')
    
    # AIS haritası (alt sol)
    ax_ais.set_title('🔴 AIS Haritası', fontsize=12, fontweight='bold')
    ax_ais.grid(True, alpha=0.3)
    if ais_points:
        ax_ais.scatter(ais_x, ais_y, c='red', s=100, alpha=0.8, marker='o')
        for i, point in enumerate(ais_points):
            ax_ais.annotate(f"{i+1}", (point['x'], point['y']), 
                          xytext=(3, 3), textcoords='offset points', fontsize=8)
    ax_ais.set_aspect('equal', adjustable='box')
    
    # Tespit haritası (alt sağ)
    ax_det.set_title('🔵 Tespit Haritası', fontsize=12, fontweight='bold')
    ax_det.grid(True, alpha=0.3)
    if detection_points:
        ax_det.scatter(det_x, det_y, c='blue', s=80, alpha=0.7, marker='^')
        for i, point in enumerate(detection_points[:20]):  # İlk 20 tane
            ax_det.annotate(f"{i+1}", (point['x'], point['y']), 
                          xytext=(3, 3), textcoords='offset points', fontsize=7)
    ax_det.set_aspect('equal', adjustable='box')
    
    # Layout ayarla
    plt.tight_layout()
    
    # Kaydet
    output_file = "visual_map.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

def print_results_summary(matches):
    """Özet sonuçları yazdır"""
    if matches:
        distances = [m['distance'] for m in matches]
        confidences = [m['confidence'] for m in matches]
        print(f"Eşleştirme: {len(matches)}, Ortalama mesafe: {sum(distances)/len(distances):.2f} km, Ortalama güven: {sum(confidences)/len(confidences):.3f}")

def process_single_image(ais_points, image_name, data_dir, max_distance=10.0):
    """Tek bir görüntüyü işle"""
    print(f"\n--- {image_name} İşleniyor ---")
    
    # Bu görüntü için tespit verilerini yükle
    detection_points = load_detection_data_per_image(data_dir, image_name)
    
    if not detection_points:
        print(f"  Tespit verisi yok")
        return None
    
    # Sabit makul ölçeklendirme uygula
    apply_coordinate_transformation(detection_points)
    
    print(f"  AIS noktaları: {len(ais_points)}")
    print(f"  Tespit noktaları: {len(detection_points)}")
    
    # Eşleştirme yap
    matches = calculate_matching(ais_points, detection_points, max_distance)
    
    if matches:
        distances = [m['distance'] for m in matches]
        confidences = [m['confidence'] for m in matches]
        print(f"  Eşleştirme: {len(matches)}, Avg mesafe: {sum(distances)/len(distances):.2f} km, Avg güven: {sum(confidences)/len(confidences):.3f}")
    else:
        print(f"  Eşleştirme bulunamadı")
    
    return {
        'image_name': image_name,
        'ais_points': ais_points,
        'detection_points': detection_points,
        'matches': matches
    }

def main():
    # AIS verilerini yükle (tüm görüntüler için aynı)
    ais_points = load_ais_data("../data/sample_ais.json")
    
    if not ais_points:
        print("AIS verisi bulunamadı!")
        return
    
    # Mevcut görüntüleri al
    available_images = get_available_images("../data")
    
    if not available_images:
        print("Hiç etiketli görüntü bulunamadı!")
        return
    
    print(f"Toplam {len(available_images)} görüntü bulundu:")
    for img in available_images:
        print(f"  - {img}")
    
    # Her görüntüyü ayrı işle
    all_results = []
    for image_name in available_images:
        result = process_single_image(ais_points, image_name, "../data")
        if result:
            all_results.append(result)
    
    # Sonuçları özetle
    print(f"\n=== GENEL ÖZET ===")
    total_matches = sum(len(r['matches']) for r in all_results)
    print(f"Toplam {len(all_results)} görüntü işlendi")
    print(f"Toplam {total_matches} eşleştirme bulundu")
    
    # İlk görüntü için görsel harita oluştur
    if all_results:
        print(f"\n--- {all_results[0]['image_name']} için görsel harita oluşturuluyor ---")
        try:
            create_visual_map(all_results[0]['ais_points'], 
                           all_results[0]['detection_points'], 
                           all_results[0]['matches'])
            print("Görsel harita oluşturuldu: visual_map.png")
        except Exception as e:
            print(f"Harita oluşturulamadı: {e}")

if __name__ == "__main__":
    main()
