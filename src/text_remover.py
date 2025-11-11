"""Text detection and removal using inpainting"""
import cv2
import numpy as np
from PIL import Image
import torch

class TextRemover:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def detect_text_regions(self, image):
        """Detect text regions using multiple methods"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # Method 1: Edge-based detection (horizontal text)
        edges = cv2.Canny(gray, 30, 100)
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        dilated_h = cv2.dilate(edges, kernel_h, iterations=3)
        contours_h, _ = cv2.findContours(dilated_h, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours_h:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            area = w * h
            if aspect_ratio > 1.5 and 50 < area < 100000 and h < 150:
                cv2.rectangle(mask, (x-10, y-10), (x+w+10, y+h+10), 255, -1)
        
        # Method 2: Vertical text detection
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 25))
        dilated_v = cv2.dilate(edges, kernel_v, iterations=3)
        contours_v, _ = cv2.findContours(dilated_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours_v:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / float(w) if w > 0 else 0
            area = w * h
            if aspect_ratio > 1.5 and 50 < area < 100000 and w < 150:
                cv2.rectangle(mask, (x-10, y-10), (x+w+10, y+h+10), 255, -1)
        
        # Method 3: High-contrast regions (typical for text)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated_small = cv2.dilate(thresh, kernel_small, iterations=2)
        contours_small, _ = cv2.findContours(dilated_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours_small:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if 30 < area < 80000:
                cv2.rectangle(mask, (x-8, y-8), (x+w+8, y+h+8), 255, -1)
        
        return mask
    
    def inpaint_text(self, image, mask):
        """Remove text using inpainting"""
        img_array = np.array(image)
        
        # Use larger radius for better inpainting
        inpainted = cv2.inpaint(img_array, mask, 15, cv2.INPAINT_TELEA)
        
        return Image.fromarray(inpainted)
    
    def remove_text(self, image):
        """Detect and remove text from image"""
        # Detect text regions
        mask = self.detect_text_regions(image)
        
        # Check if any text detected
        if np.sum(mask) == 0:
            return image, False
        
        # Inpaint text regions
        cleaned = self.inpaint_text(image, mask)
        
        return cleaned, True
