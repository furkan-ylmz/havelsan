"""
AIS-Kamera Eşleştirme Algoritması
================================
"""

import math
from typing import List, Tuple

# Hungarian algoritması için
try:
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    HUNGARIAN_AVAILABLE = True
except ImportError:
    HUNGARIAN_AVAILABLE = False

class AISPoint:
    """AIS nokta verisi"""
    def __init__(self, name: str, mmsi: str, lat: float, lon: float, x: float, y: float):
        self.name = name
        self.mmsi = mmsi  
        self.lat = lat
        self.lon = lon
        self.x = x  # 2D koordinat
        self.y = y

class DetectionPoint:
    """Tespit nokta verisi"""
    def __init__(self, id: str, x: float, y: float):
        self.id = id
        self.x = x  # 2D koordinat
        self.y = y

class Match:
    """Eslestirme sonucu"""
    def __init__(self, ais_point: AISPoint, detection_point: DetectionPoint, distance: float, confidence: float):
        self.ais_point = ais_point
        self.detection_point = detection_point
        self.distance = distance
        self.confidence = confidence

class MatchingAlgorithm:
    """Core eslestirme algoritması"""
    
    def __init__(self, max_distance: float = 5.0):
        self.max_distance = max_distance
    
    def calculate_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Oklid mesafesi"""
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def calculate_confidence(self, distance: float) -> float:
        """Guven skoru (0-1)"""
        if distance >= self.max_distance:
            return 0.0
        confidence = 1.0 - (distance / self.max_distance)
        return max(0.0, min(1.0, confidence))
    
    def simple_nearest_matching(self, ais_points: List[AISPoint], detection_points: List[DetectionPoint]) -> List[Match]:
        """En yakın komşu eşleştirmesi"""
        matches = []
        used_detections = set()
        
        for ais_point in ais_points:
            best_match = None
            best_distance = float('inf')
            
            for det_index, det_point in enumerate(detection_points):
                if det_index in used_detections:
                    continue
                
                distance = self.calculate_distance(
                    (ais_point.x, ais_point.y),
                    (det_point.x, det_point.y)
                )
                
                if distance < best_distance and distance <= self.max_distance:
                    best_distance = distance
                    best_match = (det_point, det_index)
            
            if best_match is not None:
                det_point, det_index = best_match
                confidence = self.calculate_confidence(best_distance)
                
                match = Match(ais_point, det_point, best_distance, confidence)
                matches.append(match)
                used_detections.add(det_index)
        
        return matches
    
    def hungarian_matching(self, ais_points: List[AISPoint], detection_points: List[DetectionPoint]) -> List[Match]:
        """Hungarian algoritması ile optimal eşleştirme"""
        if not HUNGARIAN_AVAILABLE or not ais_points or not detection_points:
            return self.simple_nearest_matching(ais_points, detection_points)
        
        # Maliyet matrisi oluştur
        n_ais = len(ais_points)
        n_det = len(detection_points)
        
        cost_matrix = np.full((n_ais, n_det), np.inf)
        
        for i, ais_point in enumerate(ais_points):
            for j, det_point in enumerate(detection_points):
                distance = self.calculate_distance(
                    (ais_point.x, ais_point.y),
                    (det_point.x, det_point.y)
                )
                
                if distance <= self.max_distance:
                    cost_matrix[i, j] = distance
        
        # Hungarian algoritması
        try:
            row_indices, col_indices = linear_sum_assignment(cost_matrix)
            
            matches = []
            for i, j in zip(row_indices, col_indices):
                if cost_matrix[i, j] < np.inf:
                    distance = cost_matrix[i, j]
                    confidence = self.calculate_confidence(distance)
                    
                    match = Match(ais_points[i], detection_points[j], distance, confidence)
                    matches.append(match)
            
            return matches
            
        except Exception:
            return self.simple_nearest_matching(ais_points, detection_points)

    def match(self, ais_points: List[AISPoint], detection_points: List[DetectionPoint], method: str = 'hungarian') -> List[Match]:
        """Ana eşleştirme fonksiyonu"""
        if method == 'hungarian' and HUNGARIAN_AVAILABLE:
            return self.hungarian_matching(ais_points, detection_points)
        else:
            return self.simple_nearest_matching(ais_points, detection_points)

def test_matching():
    """Test fonksiyonu"""
    ais_points = [
        AISPoint("GEMI A", "123456", 40.0, 32.0, 1.0, 1.0),
        AISPoint("GEMI B", "789012", 40.1, 32.1, 2.0, 2.0)
    ]
    
    detection_points = [
        DetectionPoint("TESPIT1", 1.1, 1.1),
        DetectionPoint("TESPIT2", 2.1, 1.9)
    ]
    
    matcher = MatchingAlgorithm()
    matches = matcher.match(ais_points, detection_points)
    
    print(f"Toplam {len(matches)} eşleştirme bulundu.")

if __name__ == "__main__":
    test_matching()
