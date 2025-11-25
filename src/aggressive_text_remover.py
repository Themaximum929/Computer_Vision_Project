"""Aggressive text removal using blur detection and multiple passes"""
import cv2
import numpy as np
from PIL import Image

class AggressiveTextRemover:
    def __init__(self):
        pass
    
    def remove_text(self, image, iterations=2):
        """Aggressively remove text with multiple passes"""
        img_array = np.array(image)
        
        for i in range(iterations):
            mask = self._detect_all_text(img_array)
            
            if np.sum(mask) == 0:
                break
            
            # Inpaint with large radius
            img_array = cv2.inpaint(img_array, mask, 20, cv2.INPAINT_TELEA)
        
        return Image.fromarray(img_array), True
    
    def _detect_all_text(self, img_array):
        """Detect all possible text regions"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # 1. Canny edges with multiple thresholds
        for low, high in [(20, 80), (40, 120), (60, 150)]:
            edges = cv2.Canny(gray, low, high)
            
            # Horizontal text
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 2))
            dilated = cv2.dilate(edges, kernel_h, iterations=4)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 5 and w/h > 1.2:
                    cv2.rectangle(mask, (x-15, y-15), (x+w+15, y+h+15), 255, -1)
            
            # Vertical text
            kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 30))
            dilated = cv2.dilate(edges, kernel_v, iterations=4)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > 20 and w > 5 and h/w > 1.2:
                    cv2.rectangle(mask, (x-15, y-15), (x+w+15, y+h+15), 255, -1)
        
        # 2. Adaptive thresholding for high-contrast text
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 2))
        dilated = cv2.dilate(adaptive, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if 20 < area < 100000:
                cv2.rectangle(mask, (x-12, y-12), (x+w+12, y+h+12), 255, -1)
        
        # 3. MSER (Maximally Stable Extremal Regions) for text-like regions
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            area = w * h
            if 30 < area < 50000 and (w/h > 1.5 or h/w > 1.5):
                cv2.rectangle(mask, (x-10, y-10), (x+w+10, y+h+10), 255, -1)
        
        return mask
