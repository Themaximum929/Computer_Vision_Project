"""Color Palette Extraction for Smart Styling"""
from PIL import Image
import numpy as np
from collections import Counter

class ColorPaletteExtractor:
    def __init__(self):
        self.dominant_colors = []
    
    def extract_palette(self, image, n_colors=5):
        """Extract dominant colors from image"""
        img = image.resize((150, 150))
        pixels = np.array(img).reshape(-1, 3)
        
        # Handle single color images
        unique_pixels = np.unique(pixels, axis=0)
        if len(unique_pixels) < n_colors:
            # Pad with the dominant color
            self.dominant_colors = [tuple(c) for c in unique_pixels]
            while len(self.dominant_colors) < n_colors:
                self.dominant_colors.append(self.dominant_colors[0])
            return self.dominant_colors
        
        # K-means clustering for dominant colors
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        counts = Counter(kmeans.labels_)
        
        # Sort by frequency
        sorted_colors = [colors[i] for i in sorted(counts, key=counts.get, reverse=True)]
        self.dominant_colors = [tuple(c) for c in sorted_colors]
        
        return self.dominant_colors
    
    def get_complementary_color(self, rgb):
        """Get complementary color for text"""
        r, g, b = rgb
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return (255, 255, 255) if brightness < 128 else (0, 0, 0)
    
    def get_accent_color(self):
        """Get accent color from palette"""
        if len(self.dominant_colors) >= 2:
            return self.dominant_colors[1]
        return (255, 215, 0)  # Gold fallback
    
    def analyze_mood_from_colors(self):
        """Analyze mood based on color palette"""
        if not self.dominant_colors:
            return "neutral"
        
        primary = self.dominant_colors[0]
        r, g, b = primary
        
        if r > 150 and g < 100 and b < 100:
            return "intense"
        elif b > 150 and r < 100:
            return "calm"
        elif r > 200 and g > 200 and b < 100:
            return "energetic"
        elif r < 80 and g < 80 and b < 80:
            return "dark"
        else:
            return "balanced"
