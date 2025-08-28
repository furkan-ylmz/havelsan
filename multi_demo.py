import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

# ==== 1. Sentetik AIS verisi ====
# Her AIS hedefi için beklenen piksel konumu ve boyutu
ais_targets = [
    {"id": "AIS-001", "pixel_pos": (320, 200), "pixel_size": 120},
    {"id": "AIS-002", "pixel_pos": (600, 220), "pixel_size": 80},
    {"id": "AIS-003", "pixel_pos": (400, 400), "pixel_size": 100}
]

# ==== 2. Görüntü yükle ====
img = cv2.imread("gemi.png")  # Test fotoğrafın

# ==== 3. Sentetik görsel tespitler ====
# Normalde tespit modeli (YOLO vb.) ile çıkarılır
detections = [
    {"bbox": (270, 360, 365, 200)}  # (x, y, w, h)
]

# ==== 4. Maliyet matrisi oluşturma ====
cost_matrix = np.zeros((len(ais_targets), len(detections)))

for i, ais in enumerate(ais_targets):
    for j, det in enumerate(detections):
        x, y, w, h = det["bbox"]
        det_center = (x + w/2, y + h/2)

        # Konum farkı (piksel)
        pos_err = np.linalg.norm(np.array(det_center) - np.array(ais["pixel_pos"]))

        # Boyut farkı (oransal)
        size_err = abs(w - ais["pixel_size"]) / ais["pixel_size"]

        # Basit skor: konum %70, boyut %30 ağırlık
        cost_matrix[i, j] = 0.7 * pos_err + 0.3 * (size_err * 100)

# ==== 5. Hungarian ile atama ====
row_ind, col_ind = linear_sum_assignment(cost_matrix)

matches = []
for r, c in zip(row_ind, col_ind):
    matches.append((ais_targets[r]["id"], detections[c]["bbox"], cost_matrix[r, c]))

# ==== 6. Sonuçları çizdir ====
for ais_id, bbox, cost in matches:
    x, y, w, h = bbox
    cv2.rectangle(img, (int(x), int(y)), (int(x+w), int(y+h)), (0, 255, 0), 2)
    cv2.putText(img, f"{ais_id} | M: {cost:.1f}", (int(x), int(y) - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # AIS beklenen konumu (kırmızı çarpı)
    px, py = [int(v) for v in ais_targets[[a["id"] for a in ais_targets].index(ais_id)]["pixel_pos"]]
    cv2.drawMarker(img, (px, py), (0, 0, 255), markerType=cv2.MARKER_CROSS, 
                   markerSize=10, thickness=2)

cv2.imshow("Coklu Aday Eslestirme Demo", img)
cv2.waitKey(0)
