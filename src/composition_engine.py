"""Advanced Composition Engine for Poster Layout"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

class CompositionEngine:
    def __init__(self):
        self.safe_zones = {}
    
    def detect_safe_zones(self, image):
        """Detect areas suitable for text placement"""
        img_array = np.array(image.convert('L'))
        h, w = img_array.shape
        
        # Divide into grid
        grid_h, grid_w = 4, 3
        cell_h, cell_w = h // grid_h, w // grid_w
        
        zones = []
        for i in range(grid_h):
            for j in range(grid_w):
                y1, y2 = i * cell_h, (i + 1) * cell_h
                x1, x2 = j * cell_w, (j + 1) * cell_w
                
                cell = img_array[y1:y2, x1:x2]
                variance = np.var(cell)
                mean = np.mean(cell)
                
                # Low variance = good for text
                score = 1.0 / (1.0 + variance / 1000)
                zones.append({
                    'bbox': (x1, y1, x2, y2),
                    'score': score,
                    'brightness': mean,
                    'position': f"{['top', 'mid-top', 'mid-bottom', 'bottom'][i]}_{['left', 'center', 'right'][j]}"
                })
        
        self.safe_zones = sorted(zones, key=lambda x: x['score'], reverse=True)
        return self.safe_zones
    
    def get_best_title_position(self, image, prefer_position="bottom"):
        """Get optimal position for title"""
        zones = self.detect_safe_zones(image)
        
        # Filter by preference
        if prefer_position == "bottom":
            candidates = [z for z in zones if 'bottom' in z['position']]
        elif prefer_position == "top":
            candidates = [z for z in zones if 'top' in z['position']]
        else:
            candidates = zones
        
        if candidates:
            best = candidates[0]
            x1, y1, x2, y2 = best['bbox']
            return ((x1 + x2) // 2, (y1 + y2) // 2), best['brightness']
        
        # Fallback
        w, h = image.size
        return (w // 2, int(h * 0.85)), 128
    
    def add_vignette(self, image, strength=0.3):
        """Add vignette effect for focus"""
        w, h = image.size
        mask = Image.new('L', (w, h), 255)
        draw = ImageDraw.Draw(mask)
        
        for i in range(int(min(w, h) * 0.3)):
            alpha = int(255 * (1 - strength * (1 - i / (min(w, h) * 0.3))))
            draw.rectangle([i, i, w-i, h-i], outline=alpha)
        
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.05))
        
        vignette = Image.new('RGB', (w, h), (0, 0, 0))
        return Image.composite(image, vignette, mask)
    
    def apply_rule_of_thirds_grid(self, image, show_grid=False):
        """Apply rule of thirds composition guide"""
        if not show_grid:
            return image
        
        img = image.copy()
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # Draw grid lines
        for i in [1, 2]:
            x = w * i // 3
            y = h * i // 3
            draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 100), width=2)
            draw.line([(0, y), (w, y)], fill=(255, 255, 255, 100), width=2)
        
        return img
