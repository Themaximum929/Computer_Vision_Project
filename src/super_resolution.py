"""Super-resolution upscaling for sharper posters"""
import cv2
import numpy as np
from PIL import Image

class SuperResolution:
    def __init__(self):
        pass
    
    def upscale(self, image, scale=1.5):
        """Upscale image using advanced techniques"""
        img_array = np.array(image)
        
        # Method 1: EDSR-style upscaling (edge-directed)
        # Use cubic interpolation with edge enhancement
        h, w = img_array.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Upscale with cubic interpolation
        upscaled = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Edge enhancement
        gray = cv2.cvtColor(upscaled, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
        
        # Sharpen edges
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        
        # Blend based on edges
        edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB) / 255.0
        result = upscaled * (1 - edges_3ch * 0.3) + sharpened * (edges_3ch * 0.3)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Downscale back to original size with LANCZOS (super-sampling anti-aliasing)
        final = cv2.resize(result, (w, h), interpolation=cv2.INTER_LANCZOS4)
        
        return Image.fromarray(final)
    
    def enhance_details(self, image):
        """Enhance fine details without upscaling"""
        img_array = np.array(image)
        
        # Bilateral filter (preserves edges while smoothing)
        filtered = cv2.bilateralFilter(img_array, 5, 50, 50)
        
        # Unsharp mask
        gaussian = cv2.GaussianBlur(filtered, (0, 0), 3.0)
        sharpened = cv2.addWeighted(filtered, 1.8, gaussian, -0.8, 0)
        
        # Detail enhancement using high-frequency boost
        high_freq = filtered.astype(float) - gaussian.astype(float)
        enhanced = filtered.astype(float) + high_freq * 0.5
        
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        return Image.fromarray(enhanced)
