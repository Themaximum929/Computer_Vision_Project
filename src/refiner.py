"""Quality Refiner Agent - Post-processing for quality enhancement"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

class QualityRefiner:
    def __init__(self):
        pass
    
    def enhance(self, image):
        """Enhanced post-processing - smooth, sharp, vibrant"""
        img_array = np.array(image)
        
        # 1. Denoise (remove graininess)
        img_array = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
        
        # 2. Bilateral filter (smooth while preserving edges)
        img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
        
        # 3. Gentle unsharp mask (sharpness without grain)
        gaussian = cv2.GaussianBlur(img_array, (0, 0), 1.5)
        img_array = cv2.addWeighted(img_array, 1.3, gaussian, -0.3, 0)
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        image = Image.fromarray(img_array)
        
        # 4. Vibrant colors (baseline style)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.15)  # More saturated
        
        # 5. Contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        
        # 6. Brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def refine(self, image):
        """Backward compatibility"""
        return self.enhance(image)
    
    def detect_and_fix_artifacts(self, image):
        """Detect and reduce common artifacts"""
        # Apply slight gaussian blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Enhance edges
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return image
