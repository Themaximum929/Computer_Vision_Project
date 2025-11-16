"""Color Intelligence - Extract and analyze colors from images"""
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import colorsys

class ColorExtractor:
    def extract_palette(self, image, n_colors=5):
        """Extract dominant colors using K-means clustering"""
        img_array = np.array(image.resize((150, 150)))  # Resize for speed
        pixels = img_array.reshape(-1, 3)
        
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(color) for color in colors]
    
    def get_contrast_color(self, bg_color):
        """Return white or black for best contrast"""
        r, g, b = bg_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)
    
    def create_complementary(self, color):
        """Generate complementary color"""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = (h + 0.5) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r*255), int(g*255), int(b*255))
    
    def create_analogous(self, color):
        """Generate analogous colors"""
        r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        colors = []
        for offset in [-0.083, 0.083]:  # ±30 degrees
            new_h = (h + offset) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            colors.append((int(r*255), int(g*255), int(b*255)))
        
        return colors
    
    def sort_by_brightness(self, colors):
        """Sort colors from dark to light"""
        def brightness(color):
            return sum(color) / 3
        return sorted(colors, key=brightness)
