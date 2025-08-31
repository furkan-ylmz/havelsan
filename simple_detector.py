import cv2
import numpy as np
from pathlib import Path
from ais_matcher import AISMatcher, AISTarget, DetectedShip, create_sample_ais_data

class SimpleDetector:
    """Basit gemi tespit sistemi"""
    
    def __init__(self):
        self.matcher = AISMatcher()
        self.own_position = (40.0, 32.0)
    
    def detect_ships_manual(self, image):
        """Manuel tespit (YOLO yerine basit yöntem)"""
        # Bu kısımda normalde YOLO çalışacak
        # Şimdilik manuel bounding box döndürelim
        detections = []
        
        # Örnek tespit (gerçekte YOLO'dan gelecek)
        height, width = image.shape[:2]
        
        # Basit edge detection ile gemi tespit etmeye çalışalım
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum alan
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 20:  # Minimum boyut
                    detection = DetectedShip((x, y, w, h), confidence=0.8)
                    detections.append(detection)
        
        return detections[:5]  # En fazla 5 tespit
    
    def process_image(self, image):
        """Görüntüyü işle ve eşleştir"""
        # Gemi tespit et
        detections = self.detect_ships_manual(image)
        
        # AIS verileri oluştur
        ais_targets = create_sample_ais_data(len(detections))
        
        # Eşleştir
        matches = self.matcher.match_targets(ais_targets, detections, self.own_position)
        
        return matches, detections
    
    def run_video(self, video_path):
        """Video üzerinde çalıştır"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Video açılamadı: {video_path}")
            return
        
        print("Video işleniyor... 'q' ile çıkış")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # İşle
            matches, detections = self.process_image(frame)
            
            # Çiz
            result = frame.copy()
            
            # Tespitleri çiz
            for detection in detections:
                x, y, w, h = detection.bbox
                cv2.rectangle(result, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Eşleştirmeleri çiz
            for ais, detection, confidence in matches:
                x, y, w, h = detection.bbox
                color = (0, 255, 0) if confidence > 0.5 else (0, 0, 255)
                cv2.rectangle(result, (x, y), (x+w, y+h), color, 2)
                cv2.putText(result, f"MMSI:{ais.mmsi}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Bilgi
            info = f"Ships: {len(detections)}, Matches: {len(matches)}"
            cv2.putText(result, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Ship Detection', result)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = SimpleDetector()
    
    # Video dosyası test et
    video_files = ["data/videos/1.mp4", "data/videos/2.mp4", "data/videos/3.mp4", "data/videos/4.mp4"]
    
    for video in video_files:
        if Path(video).exists():
            print(f"\n{video} testi:")
            detector.run_video(video)
            break
    else:
        print("Video dosyası bulunamadı!")
