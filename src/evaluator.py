"""Quality evaluation metrics for generated posters"""
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

class PosterEvaluator:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])
    
    def aesthetic_score(self, image):
        """Simple aesthetic scoring based on color distribution"""
        img_array = np.array(image)
        
        # Color variance (higher = more diverse)
        color_var = np.var(img_array, axis=(0, 1)).mean()
        
        # Brightness balance
        brightness = np.mean(img_array)
        brightness_score = 1 - abs(brightness - 127.5) / 127.5
        
        return {
            "color_variance": float(color_var),
            "brightness_balance": float(brightness_score),
            "overall": float((color_var / 1000 + brightness_score) / 2)
        }
    
    def resolution_check(self, image, target_width=720, target_height=1280):
        """Check if image meets resolution requirements"""
        w, h = image.size
        return {
            "width": w,
            "height": h,
            "meets_target": w == target_width and h == target_height
        }
    
    def evaluate(self, image_path):
        """Full evaluation of generated poster"""
        image = Image.open(image_path)
        
        results = {
            "aesthetic": self.aesthetic_score(image),
            "resolution": self.resolution_check(image),
            "instruction_following": self.resolution_check(image)["meets_target"]
        }
        
        return results
