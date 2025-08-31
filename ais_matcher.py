import numpy as np
import cv2
import json
import math
from scipy.optimize import linear_sum_assignment
from pathlib import Path
from typing import List, Tuple, Optional

class AISTarget:
    """AIS hedef bilgileri"""
    def __init__(self, mmsi: int, lat: float, lon: float, length: float, width: float):
        self.mmsi = mmsi
        self.lat = lat
        self.lon = lon
        self.length = length
        self.width = width

class DetectedShip:
    """Tespit edilen gemi bilgileri"""
    def __init__(self, bbox: tuple, confidence: float = 1.0):
        self.bbox = bbox  # (x, y, w, h)
        self.confidence = confidence
        self.center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
        self.area = bbox[2] * bbox[3]
        self.aspect_ratio = bbox[2] / bbox[3] if bbox[3] > 0 else 1.0

class AISMatcher:
    """Basit AIS-Kamera eşleştirici"""
    
    def __init__(self, camera_params: dict = None):
        # Basit kamera parametreleri
        if camera_params is None:
            camera_params = {'fx': 1600, 'fy': 1600, 'cx': 960, 'cy': 540}
        
        self.fx = camera_params['fx']
        self.fy = camera_params['fy']
        self.cx = camera_params['cx']
        self.cy = camera_params['cy']
        
        self.max_distance = 2000  # Maksimum eşleştirme mesafesi (piksel) - artırıldı
    
    def project_ais_to_pixel(self, ais_target: AISTarget, own_position: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """AIS hedefini piksel koordinatlarına projekte eder"""
        own_lat, own_lon = own_position
        
        # Basitleştirilmiş projeksiyon
        lat_diff = ais_target.lat - own_lat
        lon_diff = ais_target.lon - own_lon
        
        # Yaklaşık mesafe (metre)
        distance_m = math.sqrt((lat_diff * 111000)**2 + (lon_diff * 111000 * math.cos(math.radians(own_lat)))**2)
        
        if distance_m == 0:
            return None
        
        # Açı hesabı
        bearing = math.atan2(lon_diff, lat_diff)
        
        # 3D projeksiyon (basit)
        x_world = distance_m * math.sin(bearing)
        y_world = distance_m * math.cos(bearing)
        
        if y_world <= 0:  # Arkada
            return None
        
        # Piksel koordinatları
        pixel_x = (self.fx * x_world / y_world) + self.cx
        pixel_y = self.cy  # Basitleştirilmiş
        
        return pixel_x, pixel_y
    
    def calculate_match_score(self, ais_target: AISTarget, detection: DetectedShip, projected_pos: Tuple[float, float]) -> float:
        """Eşleştirme skoru hesaplar (0-1 arası)"""
        proj_x, proj_y = projected_pos
        det_x, det_y = detection.center
        
        # Pozisyon hatası
        distance = math.sqrt((proj_x - det_x)**2 + (proj_y - det_y)**2)
        
        if distance > self.max_distance:
            return 0.0
        
        # Basit skor: mesafe ne kadar az o kadar iyi
        score = max(0, 1 - distance / self.max_distance)
        
        return score * detection.confidence
    
    def match_targets(self, ais_targets: List[AISTarget], detections: List[DetectedShip], own_position: Tuple[float, float]) -> List[tuple]:
        """AIS hedefleri ile tespitleri eşleştirir"""
        if not ais_targets or not detections:
            return []
        
        # AIS hedeflerini projekte et
        projections = []
        valid_ais = []
        
        for ais_target in ais_targets:
            projection = self.project_ais_to_pixel(ais_target, own_position)
            if projection is not None:
                projections.append(projection)
                valid_ais.append(ais_target)
        
        if not projections:
            return []
        
        # Maliyet matrisi
        cost_matrix = np.full((len(valid_ais), len(detections)), np.inf)
        
        for i, (ais_target, projection) in enumerate(zip(valid_ais, projections)):
            for j, detection in enumerate(detections):
                score = self.calculate_match_score(ais_target, detection, projection)
                cost_matrix[i, j] = 1 - score  # Hungarian minimizasyon yapar
        
        # Optimal eşleştirme
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        
        # Sonuçları döndür
        matches = []
        for i, j in zip(row_indices, col_indices):
            if cost_matrix[i, j] < 1.0:  # Geçerli eşleştirme
                confidence = 1 - cost_matrix[i, j]
                matches.append((valid_ais[i], detections[j], confidence))
        
        return matches

def load_yolo_annotations(txt_path, image_path):
    """YOLO formatından gemi tespitlerini yükler"""
    ships = []
    
    # Görüntü boyutlarını al
    image = cv2.imread(str(image_path))
    if image is None:
        return ships
    
    img_height, img_width = image.shape[:2]
    
    # YOLO formatını oku
    if not Path(txt_path).exists():
        return ships
    
    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                continue
            
            class_id, center_x, center_y, width, height = map(float, parts)
            
            # Normalize edilmiş koordinatları pixel'e çevir
            x = (center_x - width/2) * img_width
            y = (center_y - height/2) * img_height
            w = width * img_width
            h = height * img_height
            
            bbox = (int(x), int(y), int(w), int(h))
            ships.append(DetectedShip(bbox))
    
    return ships

def load_labelme_annotations(json_path):
    """LabelMe JSON'dan gemi tespitlerini yükler (eski format için)"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    ships = []
    for shape in data.get('shapes', []):
        if shape['label'] == 'ship':
            points = shape['points']
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            bbox = (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))
            ships.append(DetectedShip(bbox))
    
    return ships

def create_sample_ais_data(num_ships: int = 3, base_position: Tuple[float, float] = (40.0, 32.0)) -> List[AISTarget]:
    """Örnek AIS verisi oluşturur"""
    base_lat, base_lon = base_position
    ais_targets = []
    
    for i in range(num_ships):
        lat_offset = np.random.uniform(-0.01, 0.01)
        lon_offset = np.random.uniform(-0.01, 0.01)
        
        ais_target = AISTarget(
            mmsi=123456000 + i,
            lat=base_lat + lat_offset,
            lon=base_lon + lon_offset,
            length=np.random.uniform(50, 200),
            width=np.random.uniform(10, 30)
        )
        ais_targets.append(ais_target)
    
    return ais_targets

def visualize_matches(image: np.ndarray, matches: List[tuple]) -> np.ndarray:
    """Eşleştirme sonuçlarını görselleştirir"""
    result = image.copy()
    
    for ais_target, detection, confidence in matches:
        x, y, w, h = detection.bbox
        
        # Güven seviyesine göre renk
        if confidence > 0.7:
            color = (0, 255, 0)  # Yeşil
        elif confidence > 0.4:
            color = (0, 165, 255)  # Turuncu
        else:
            color = (0, 0, 255)  # Kırmızı
        
        # Bounding box çiz
        cv2.rectangle(result, (x, y), (x+w, y+h), color, 2)
        
        # Etiket
        label = f"MMSI:{ais_target.mmsi} ({confidence:.2f})"
        cv2.putText(result, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result

def process_test_data(data_dir="data"):
    """Test verilerini işler - YOLO formatı öncelikli"""
    data_path = Path(data_dir)
    txt_path = data_path / "txt"
    json_path = data_path / "json"
    matcher = AISMatcher()
    own_position = (40.0, 32.0)
    
    # Önce YOLO formatı var mı kontrol et
    use_yolo = txt_path.exists() and len(list(txt_path.glob("*.txt"))) > 0
    
    if use_yolo:
        print("YOLO formatı kullanılıyor (data/txt/)...")
        image_files = list(txt_path.glob("*.jpg"))
        
        total_ships = 0
        total_matches = 0
        
        for image_path in image_files:
            txt_file = image_path.with_suffix('.txt')
            
            if not txt_file.exists():
                continue
            
            # YOLO formatından tespitleri yükle
            detections = load_yolo_annotations(txt_file, image_path)
            
            # AIS verisi oluştur
            ais_targets = create_sample_ais_data(len(detections))
            
            # Eşleştirme yap
            matches = matcher.match_targets(ais_targets, detections, own_position)
            
            total_ships += len(detections)
            total_matches += len(matches)
            
            print(f"{image_path.name}: {len(detections)} gemi, {len(matches)} eşleştirme")
            
            # İlk 3 eşleştirmeyi göster
            for i, (ais, det, conf) in enumerate(matches[:3]):
                print(f"  {i+1}. MMSI={ais.mmsi}, Güven={conf:.3f}")
    
    elif json_path.exists():
        print("LabelMe formatı kullanılıyor (data/json/)...")
        json_files = list(json_path.glob("*.json"))
        
        total_ships = 0
        total_matches = 0
        
        for json_file in json_files:
            image_file = json_file.with_suffix('.jpg')
            
            if not image_file.exists():
                continue
            
            # LabelMe formatından tespitleri yükle
            detections = load_labelme_annotations(json_file)
            
            # AIS verisi oluştur
            ais_targets = create_sample_ais_data(len(detections))
            
            # Eşleştirme yap
            matches = matcher.match_targets(ais_targets, detections, own_position)
            
            total_ships += len(detections)
            total_matches += len(matches)
            
            print(f"{image_file.name}: {len(detections)} gemi, {len(matches)} eşleştirme")
            
            # İlk 3 eşleştirmeyi göster
            for i, (ais, det, conf) in enumerate(matches[:3]):
                print(f"  {i+1}. MMSI={ais.mmsi}, Güven={conf:.3f}")
    
    else:
        print("❌ Veri bulunamadı! data/txt/ veya data/json/ klasörlerini kontrol edin.")
        return
    
    print(f"\nToplam: {total_ships} gemi, {total_matches} eşleştirme")
    print(f"Başarı oranı: {total_matches/total_ships*100:.1f}%" if total_ships > 0 else "Başarı oranı: 0%")

if __name__ == "__main__":
    print("🚢 AIS-Kamera Eşleştirme - Basit Versiyon")
    print("=" * 40)
    
    # Test verilerini işle
    process_test_data()
