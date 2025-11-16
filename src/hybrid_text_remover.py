"""Hybrid text removal: OCR for large text + Edge detection for small text"""
import cv2
import numpy as np
from PIL import Image

class HybridTextRemover:
    def __init__(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=True)
            self.has_ocr = True
        except:
            self.has_ocr = False
    
    def remove_text(self, image, iterations=2, repair=True):
        """Hybrid: OCR for large text + Edge detection for small text"""
        img_array = np.array(image)
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        
        # Step 1: OCR for large/clear text (titles, credits)
        if self.has_ocr:
            ocr_mask = self._detect_ocr(img_array)
            mask = cv2.bitwise_or(mask, ocr_mask)
        
        # Step 2: Edge detection for small/distorted text
        for _ in range(iterations):
            edge_mask = self._detect_edges(img_array)
            mask = cv2.bitwise_or(mask, edge_mask)
        
        # Step 3: Inpaint with advanced method
        if np.sum(mask) > 0:
            img_array = self._advanced_inpaint(img_array, mask)
            
            # Step 4: Repair distortions
            if repair:
                img_array = self._repair_inpainted_regions(img_array, mask)
            
            return Image.fromarray(img_array), True
        
        return image, False
    
    def _detect_ocr(self, img_array):
        """OCR detection for large text"""
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        results = self.reader.readtext(img_array)
        
        for (bbox, text, prob) in results:
            if prob > 0.3:  # Confidence threshold
                pts = np.array(bbox, dtype=np.int32)
                pts = (pts * 1.15).astype(np.int32)  # Expand 15%
                cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def _detect_edges(self, img_array):
        """Edge detection for small/distorted text"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # Multi-threshold edge detection
        for low, high in [(30, 90), (50, 120)]:
            edges = cv2.Canny(gray, low, high)
            
            # Horizontal text
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 2))
            dilated = cv2.dilate(edges, kernel_h, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 15 and h > 3 and w/h > 1.2:  # Small text
                    cv2.rectangle(mask, (x-10, y-10), (x+w+10, y+h+10), 255, -1)
        
        # MSER for distorted text
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            area = w * h
            if 20 < area < 30000 and (w/h > 1.3 or h/w > 1.3):
                cv2.rectangle(mask, (x-8, y-8), (x+w+8, y+h+8), 255, -1)
        
        return mask
    
    def _advanced_inpaint(self, img_array, mask):
        """Multi-pass inpainting for better quality"""
        result = cv2.inpaint(img_array, mask, 25, cv2.INPAINT_TELEA)
        return result
    
    def _repair_inpainted_regions(self, img_array, mask):
        """Repair distortions with aggressive smoothing"""
        # Expand mask for repair zone
        kernel = np.ones((25, 25), np.uint8)
        expanded_mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Heavy bilateral filtering on expanded region
        smoothed = cv2.bilateralFilter(img_array, 15, 100, 100)
        
        # Create gradient blend mask
        distance = cv2.distanceTransform(255 - expanded_mask, cv2.DIST_L2, 5)
        distance = cv2.normalize(distance, None, 0, 1, cv2.NORM_MINMAX)
        blend_mask = np.stack([distance]*3, axis=-1)
        
        # Blend smoothed with original
        result = img_array * blend_mask + smoothed * (1 - blend_mask)
        
        # Apply non-local means denoising
        result = cv2.fastNlMeansDenoisingColored(result.astype(np.uint8), None, 8, 8, 7, 21)
        
        return result
