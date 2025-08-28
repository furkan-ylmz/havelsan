import numpy as np
import cv2
from pyproj import Transformer
from scipy.optimize import linear_sum_assignment

# ======================
# 1. Kamera ve gemi parametreleri
# ======================

# Kamera iç parametreleri
fx, fy = 1600, 1600      # Odak uzaklığı (piksel)
cx, cy = 960, 540        # Optik merkez (piksel)
dist_coeffs = np.zeros(5)

# Kameranın gemiye göre konumu ve yönü
camera_pos_ship = np.array([0, 0, 10])  # metre
camera_rot_ship = np.eye(3)  # Basitlik için yönelim = kimlik matrisi

# Kendi geminin GNSS konumu
own_lat, own_lon = 40.0, 32.0

# ENU dönüşüm ayarları
transformer = Transformer.from_crs("EPSG:4326", "EPSG:4978")

# ======================
# 2. Yardımcı fonksiyonlar
# ======================

def ecef_to_enu(rel_ecef, lat0, lon0):
    """ECEF fark vektörünü ENU'ya çevirir."""
    lat0, lon0 = np.radians(lat0), np.radians(lon0)
    slat, clat = np.sin(lat0), np.cos(lat0)
    slon, clon = np.sin(lon0), np.cos(lon0)
    R = np.array([
        [-slon,  clon,     0],
        [-clon*slat, -slon*slat, clat],
        [clon*clat,  slon*clat,  slat]
    ])
    return R @ rel_ecef

def ship_to_camera(vec_ship, cam_pos, cam_rot):
    """Gemi koordinatlarından kamera koordinatlarına çevirir."""
    return cam_rot @ (vec_ship - cam_pos)

def ais_to_pixel(lat, lon, L_real, own_lat, own_lon):
    """AIS konumundan beklenen piksel konumu ve piksel boyunu hesaplar."""
    ais_ecef = np.array(transformer.transform(lat, lon, 0))
    own_ecef = np.array(transformer.transform(own_lat, own_lon, 0))
    rel_ecef = ais_ecef - own_ecef
    rel_enu = ecef_to_enu(rel_ecef, own_lat, own_lon)
    rel_cam = ship_to_camera(rel_enu, camera_pos_ship, camera_rot_ship)

    if rel_cam[2] <= 0:
        return None, None  # Kamera arkasında

    x = (fx * rel_cam[0] / rel_cam[2]) + cx
    y = (fy * rel_cam[1] / rel_cam[2]) + cy
    pixel_size = fx * L_real / rel_cam[2]

    return (x, y), pixel_size

def match_targets(ais_targets, detections):
    """AIS hedefleri ile tespitler arasında Hungarian ataması yapar."""
    cost_matrix = np.full((len(ais_targets), len(detections)), np.inf)

    for i, ais in enumerate(ais_targets):
        for j, det in enumerate(detections):
            # Konum farkı
            pos_err = np.linalg.norm(np.array(det['center']) - np.array(ais['pixel_pos']))
            # Boyut farkı (oransal)
            size_err_ratio = abs(det['width'] - ais['pixel_size']) / ais['pixel_size']
            # Basit ağırlıklı skor
            cost = 0.7 * pos_err + 0.3 * (size_err_ratio * 100)  # boyutu % cinsinden hata
            cost_matrix[i, j] = cost

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    matches = []
    for r, c in zip(row_ind, col_ind):
        if np.isfinite(cost_matrix[r, c]):
            matches.append((r, c, cost_matrix[r, c]))

    return matches

# ======================
# 3. Örnek veri
# ======================

# AIS hedefleri (lat, lon, uzunluk metre)
ais_data = [
    {'lat': 40.005, 'lon': 32.004, 'length': 120.0},
    {'lat': 40.007, 'lon': 32.002, 'length': 80.0}
]

# Görsel tespitler (bounding box: x, y, w, h)
detections = [
    {'center': (950, 500), 'width': 78, 'height': 40},
    {'center': (1100, 520), 'width': 60, 'height': 30}
]

# ======================
# 4. AIS projeksiyon
# ======================
ais_targets = []
for ais in ais_data:
    px_pos, px_size = ais_to_pixel(ais['lat'], ais['lon'], ais['length'],
                                   own_lat, own_lon)
    if px_pos:
        ais_targets.append({
            'pixel_pos': px_pos,
            'pixel_size': px_size
        })

# ======================
# 5. Eşleştirme
# ======================
matches = match_targets(ais_targets, detections)

# ======================
# 6. Çıktı
# ======================
for ais_idx, det_idx, cost in matches:
    print(f"AIS hedef #{ais_idx} ↔ Tespit #{det_idx} | Maliyet: {cost:.2f}")
