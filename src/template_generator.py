"""
Automatic Template Generator - Level 3 Innovation
Generates poster layouts dynamically based on content and design rules
"""
import random
from typing import Dict, List, Tuple

class TemplateGenerator:
    """Generate poster templates using design principles"""
    
    POSTER_SIZES = {
        'standard': (720, 1080),
        'wide': (1080, 720),
        'square': (1080, 1080),
        'instagram': (1080, 1350)
    }
    
    LAYOUT_RULES = {
        'movie': {'image_ratio': 0.7, 'text_bottom': True, 'margin': 0.05},
        'music': {'image_ratio': 0.6, 'text_bottom': False, 'margin': 0.08},
        'event': {'image_ratio': 0.65, 'text_bottom': True, 'margin': 0.06},
        'sports': {'image_ratio': 0.75, 'text_bottom': True, 'margin': 0.04},
    }
    
    def generate(self, genre: str = 'movie', size_type: str = 'standard') -> Dict:
        """Generate template based on genre and size"""
        w, h = self.POSTER_SIZES.get(size_type, (720, 1080))
        rules = self.LAYOUT_RULES.get(genre, self.LAYOUT_RULES['movie'])
        
        margin = int(min(w, h) * rules['margin'])
        
        # Calculate image region
        img_h = int(h * rules['image_ratio'])
        img_bbox = [margin, margin, w - margin, margin + img_h]
        
        # Calculate text region
        if rules['text_bottom']:
            text_y = margin + img_h + margin
            text_bbox = [margin * 2, text_y, w - margin * 2, h - margin]
        else:
            text_bbox = [margin * 2, margin, w - margin * 2, margin + 60]
        
        return {
            'size': [w, h],
            'genre': genre,
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': img_bbox},
                {'name': 'Text', 'bbox': text_bbox}
            ]
        }
    
    def generate_multi_layout(self, genre: str = 'movie') -> Dict:
        """Generate complex multi-region layout"""
        w, h = 720, 1080
        margin = 40
        
        layouts = {
            'split': self._split_layout(w, h, margin),
            'grid': self._grid_layout(w, h, margin),
            'hero': self._hero_layout(w, h, margin)
        }
        
        layout_type = random.choice(list(layouts.keys()))
        return layouts[layout_type]
    
    def _split_layout(self, w, h, margin):
        """Split screen layout"""
        mid = h // 2
        return {
            'size': [w, h],
            'layout_type': 'split',
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin, w - margin, mid - margin]},
                {'name': 'Text', 'bbox': [margin * 2, mid + margin, w - margin * 2, h - margin]}
            ]
        }
    
    def _grid_layout(self, w, h, margin):
        """Grid-based layout"""
        return {
            'size': [w, h],
            'layout_type': 'grid',
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin * 3, w - margin, h - margin * 8]},
                {'name': 'Text', 'bbox': [margin * 2, h - margin * 7, w - margin * 2, h - margin]}
            ]
        }
    
    def _hero_layout(self, w, h, margin):
        """Hero image with overlay text"""
        return {
            'size': [w, h],
            'layout_type': 'hero',
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [0, 0, w, h]},  # Full bleed
                {'name': 'Text', 'bbox': [margin * 3, h - margin * 10, w - margin * 3, h - margin * 2]}
            ]
        }
