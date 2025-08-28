import numpy as np
import cv2
from pyproj import Transformer

# Kameranın iç parametreleri (örnek değerler)
fx, fy = 1600, 1600  # odak uzaklığı (piksel)
cx, cy = 960, 540    # optik merkez (piksel)
dist_coeffs = np.zeros(5)  # distorsiyon katsayıları (varsayılan)

# Kamera dış parametreleri (gemideki konum/yön)
camera_pos_ship = np.array([0, 0, 10])  # metre cinsinden (x,y,z)
camera_rot_ship = ...  # yaw, pitch, roll -> dönüşüm matrisi

# AIS -> ENU dönüştürücü (geminin GNSS konumu orijin)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:4978")  # WGS84 -> ECEF
# ECEF -> ENU dönüşümü kendin tanımlayacaksın

def ais_to_pixel(lat, lon, L_real, own_lat, own_lon):
    # 1. AIS konumunu ENU koordinatlarına çevir
    ais_ecef = np.array(transformer.transform(lat, lon, 0))
    own_ecef = np.array(transformer.transform(own_lat, own_lon, 0))
    rel_ecef = ais_ecef - own_ecef
    rel_enu = ecef_to_enu(rel_ecef, own_lat, own_lon)  # senin yazacağın fonksiyon

    # 2. Kameraya göre konum (dış parametre dönüşümü)
    rel_cam = ship_to_camera(rel_enu, camera_pos_ship, camera_rot_ship)

    # 3. Pinhole projeksiyon
    x = (fx * rel_cam[0] / rel_cam[2]) + cx
    y = (fy * rel_cam[1] / rel_cam[2]) + cy

    # 4. Piksel boyu tahmini (uzunluk)
    pixel_size = fx * L_real / rel_cam[2]

    return (x, y), pixel_size

# === Kullanım ===
own_lat, own_lon = 40.0, 32.0  # kendi geminin konumu
ais_lat, ais_lon = 40.005, 32.004
L_real = 120.0  # metre (AIS A+B)
pixel_pos, pixel_size_expected = ais_to_pixel(ais_lat, ais_lon, L_real, own_lat, own_lon)

# Görüntüde tespit edilen kutu
det_box = (950, 500, 80, 40)  # (x, y, w, h)
det_center = (det_box[0] + det_box[2]/2, det_box[1] + det_box[3]/2)

# Konum farkı (piksel)
pos_err = np.linalg.norm(np.array(det_center) - np.array(pixel_pos))

# Boyut farkı (oran)
size_err_ratio = abs(det_box[2] - pixel_size_expected) / pixel_size_expected

print(f"Konum hatası: {pos_err:.1f} px, Boyut oran hatası: {size_err_ratio:.2%}")
