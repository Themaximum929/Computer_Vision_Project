"""Quality Refiner Agent - Post-processing for quality enhancement"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

class QualityRefiner:
    def __init__(self):
        pass
    
    def refine(self, image):
        """Apply post-processing refinements with film-like color grading"""
        # Film-like color grading - reduce oversaturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.9)  # Slightly desaturate for natural look
        
        # Enhance contrast for depth
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        
        # Subtle sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # Warm/cool color balance
        img_array = np.array(image).astype(float)
        # Slight warm tint (reduce blue, boost red/yellow)
        img_array[:,:,2] *= 0.95  # Reduce blue slightly
        img_array[:,:,0] *= 1.02  # Boost red slightly
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        image = Image.fromarray(img_array)
        
        return image
    
    def detect_and_fix_artifacts(self, image):
        """Detect and reduce common artifacts"""
        # Apply slight gaussian blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Enhance edges
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return image
