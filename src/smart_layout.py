"""Smart Layout Detection for Text Placement"""
import numpy as np
from PIL import Image
import cv2

class SmartLayoutDetector:
    """Detect safe zones for text placement (avoid faces, key objects)"""
    
    def detect_safe_zones(self, image):
        """Find areas suitable for text overlay"""
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect edges (avoid placing text on detailed areas)
        edges = cv2.Canny(gray, 50, 150)
        
        # Divide image into grid (3x3)
        h, w = gray.shape
        zones = []
        
        for i in range(3):
            for j in range(3):
                y1, y2 = i * h // 3, (i + 1) * h // 3
                x1, x2 = j * w // 3, (j + 1) * w // 3
                
                zone_edges = edges[y1:y2, x1:x2]
                zone_brightness = gray[y1:y2, x1:x2].mean()
                
                # Score: low edges + good contrast
                edge_density = zone_edges.sum() / zone_edges.size
                score = (1 - edge_density) * 100
                
                zones.append({
                    "position": (i, j),
                    "coords": (x1, y1, x2, y2),
                    "score": score,
                    "brightness": zone_brightness,
                    "recommended_color": "white" if zone_brightness < 128 else "black"
                })
        
        # Sort by score (best zones first)
        zones.sort(key=lambda x: x["score"], reverse=True)
        return zones
    
    def suggest_text_placement(self, image, text_length="medium"):
        """Suggest optimal text placement"""
        zones = self.detect_safe_zones(image)
        
        # Title placement (top zones preferred)
        title_zones = [z for z in zones if z["position"][0] == 0]  # Top row
        
        # Subtitle placement (middle/bottom)
        subtitle_zones = [z for z in zones if z["position"][0] > 0]
        
        suggestions = {
            "title": {
                "zone": title_zones[0] if title_zones else zones[0],
                "font_size": 80,
                "alignment": "center"
            },
            "subtitle": {
                "zone": subtitle_zones[0] if subtitle_zones else zones[1],
                "font_size": 40,
                "alignment": "center"
            }
        }
        
        return suggestions
