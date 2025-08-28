import cv2
import numpy as np

# --- Simüle AIS ---
ais_pixel_pos = (320, 200)      # Beklenen piksel konumu
ais_pixel_size = 120            # Beklenen piksel genişliği

# --- Görüntü yükle ---
img = cv2.imread('gemi.jpg')

# --- Elle/otomatik tespit edilen kutu ---
det_box = (300, 180, 130, 60)   # (x, y, w, h)
det_center = (det_box[0]+det_box[2]//2, det_box[1]+det_box[3]//2)

# --- Skor hesaplama ---
pos_err = np.linalg.norm(np.array(det_center) - np.array(ais_pixel_pos))
size_err_ratio = abs(det_box[2] - ais_pixel_size) / ais_pixel_size
score = 1 / (1 + pos_err + size_err_ratio*50)

# --- Çizimler ---
cv2.circle(img, ais_pixel_pos, 5, (0,0,255), -1)
x,y,w,h = det_box
cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
cv2.putText(img, f"Skor: {score:.2f}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

cv2.imshow("Eslestirme Demo", img)
cv2.waitKey(0)
