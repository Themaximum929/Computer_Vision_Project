"""AI Layout Generator - LayoutGAN-like with Rule-based Constraints"""
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont
from src.color_contrast import get_average_color, adjust_text_color
import cv2

class AILayoutGenerator:
    """Hybrid layout generator: Rule-based + ML-ready architecture"""
    
    def __init__(self, poster_size=(720, 1080), border=50):
        self.W, self.H = poster_size
        self.border = border
        self.fonts = ['Graduate-Regular.ttf', 'Montserrat-Regular.ttf', 'Lato-Bold.ttf', 
                      'PlayfairDisplay-Regular.ttf', 'IBMPlexSerif-Regular.ttf']
    
    def detect_subject_bbox(self, image):
        """Detect main subject using saliency detection"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        _, saliency_map = saliency.computeSaliency(img_array)
        saliency_map = (saliency_map * 255).astype("uint8")
        _, thresh = cv2.threshold(saliency_map, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return (x, y, x+w, y+h)
        return (image.width//4, image.height//4, 3*image.width//4, 3*image.height//4)
    
    def apply_composition_rule(self, subject_bbox, img_size, rule='golden'):
        """Apply golden ratio or rule of thirds"""
        x1, y1, x2, y2 = subject_bbox
        w, h = img_size
        cx, cy = (x1+x2)//2, (y1+y2)//2
        
        if rule == 'golden':
            target_x = int(w * 0.618)
            target_y = int(h * 0.618)
        else:  # rule of thirds
            target_x = w // 3 if cx < w//2 else 2*w//3
            target_y = h // 3 if cy < h//2 else 2*h//3
        
        offset_x = target_x - cx
        offset_y = target_y - cy
        return offset_x, offset_y
    
    def find_empty_regions(self, image, img_bbox):
        """Find empty regions for text placement"""
        regions = []
        # Top region
        if img_bbox[1] > 150:
            regions.append(('top', [self.border, self.border, self.W-self.border, img_bbox[1]-20]))
        # Bottom region
        if self.H - img_bbox[3] > 150:
            regions.append(('bottom', [self.border, img_bbox[3]+20, self.W-self.border, self.H-self.border]))
        # Left region
        if img_bbox[0] > 150:
            regions.append(('left', [self.border, img_bbox[1], img_bbox[0]-20, img_bbox[3]]))
        # Right region
        if self.W - img_bbox[2] > 150:
            regions.append(('right', [img_bbox[2]+20, img_bbox[1], self.W-self.border, img_bbox[3]]))
        return regions
    
    def generate_text_layout(self, image, img_bbox, title, captions):
        """Generate optimal text layout with constraints"""
        empty_regions = self.find_empty_regions(image, img_bbox)
        
        # Choose placement strategy
        if empty_regions:
            return self._place_in_empty_region(image, empty_regions, title, captions)
        else:
            return self._place_with_constraints(image, img_bbox, title, captions)
    
    def _place_in_empty_region(self, image, regions, title, captions):
        """Place text in empty regions"""
        region_name, bbox = random.choice(regions)
        x1, y1, x2, y2 = bbox
        
        # Title placement
        font_size = random.randint(100, 250)
        font_family = random.choice(self.fonts)
        
        if region_name in ['top', 'bottom']:
            align = 'center'
            title_x = self.W // 2
            title_y = (y1 + y2) // 2
        else:
            align = 'left' if region_name == 'left' else 'right'
            title_x = x1 + self.border if align == 'left' else x2 - self.border
            title_y = (y1 + y2) // 2
        
        bg_color = get_average_color(image, bbox)
        text_color = adjust_text_color(bg_color, (255, 255, 255))
        
        layouts = [{
            'text': title, 'x': title_x, 'y': title_y, 'size': font_size,
            'font': font_family, 'color': text_color, 'align': align
        }]
        
        # Caption placement
        num_captions = random.choice([0, 1, 2])
        for i in range(min(num_captions, len(captions))):
            cap_y = title_y + 100 + i * 60
            layouts.append({
                'text': captions[i], 'x': title_x, 'y': cap_y,
                'size': max(20, font_size//2), 'font': font_family,
                'color': text_color, 'align': align
            })
        
        return layouts
    
    def _place_with_constraints(self, image, img_bbox, title, captions):
        """Place text with alignment constraints"""
        section = random.randint(0, 2)  # 0=left, 1=center, 2=right
        
        if section == 0:  # Left
            align = 'left'
            title_x = self.border
        elif section == 2:  # Right
            align = 'right'
            title_x = self.W - self.border
        else:  # Center
            align = 'center'
            title_x = self.W // 2
        
        title_y = random.randint(self.border, self.H - 300)
        font_size = random.randint(100, 250)
        font_family = random.choice(self.fonts)
        
        # Get background color at title position
        sample_bbox = [max(0, title_x-50), max(0, title_y-50), 
                       min(self.W, title_x+50), min(self.H, title_y+50)]
        bg_color = get_average_color(image, sample_bbox)
        text_color = adjust_text_color(bg_color, (255, 255, 255))
        
        layouts = [{
            'text': title, 'x': title_x, 'y': title_y, 'size': font_size,
            'font': font_family, 'color': text_color, 'align': align
        }]
        
        # Caption alignment rules
        num_captions = random.choice([0, 1, 2])
        for i in range(min(num_captions, len(captions))):
            cap_align = random.choice(['left', 'center', 'right']) if align != 'center' else 'center'
            
            if cap_align == 'left':
                cap_x = title_x if align == 'left' else self.border
            elif cap_align == 'right':
                cap_x = title_x if align == 'right' else self.W - self.border
            else:
                cap_x = self.W // 2
            
            cap_y = title_y + 100 + i * 60
            cap_bg = get_average_color(image, [max(0, cap_x-50), max(0, cap_y-50),
                                               min(self.W, cap_x+50), min(self.H, cap_y+50)])
            cap_color = adjust_text_color(cap_bg, (255, 255, 255))
            
            layouts.append({
                'text': captions[i], 'x': cap_x, 'y': cap_y,
                'size': max(20, font_size//2), 'font': font_family,
                'color': cap_color, 'align': cap_align
            })
        
        return layouts

class LayoutGANLite:
    """Lightweight GAN-like layout generator (ML-ready)"""
    
    def __init__(self):
        self.feature_dim = 128
        # Placeholder for future ML model
        self.model = None
    
    def encode_constraints(self, img_bbox, poster_size, keywords):
        """Encode layout constraints as feature vector"""
        W, H = poster_size
        x1, y1, x2, y2 = img_bbox
        features = [
            x1/W, y1/H, x2/W, y2/H,  # Normalized image bbox
            (x2-x1)/W, (y2-y1)/H,     # Image aspect
            len(keywords.split()),     # Keyword count
            *[0] * (self.feature_dim - 7)  # Padding for future features
        ]
        return np.array(features[:self.feature_dim])
    
    def generate_layout(self, constraints):
        """Generate layout from constraints (rule-based fallback)"""
        # TODO: Replace with trained model inference
        # For now, return random valid layout
        return {
            'title_x': random.uniform(0.1, 0.9),
            'title_y': random.uniform(0.7, 0.9),
            'title_size': random.uniform(0.1, 0.25),
            'num_captions': random.choice([0, 1, 2]),
            'alignment': random.choice(['left', 'center', 'right'])
        }
