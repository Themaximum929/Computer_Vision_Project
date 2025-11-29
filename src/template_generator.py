"""Automatic Template Generator - Level 3 Innovation"""
import random
from typing import Dict

class TemplateGenerator:
    """Generate diverse poster layouts using design principles"""
    
    LAYOUT_TYPES = ['split', 'grid', 'hero', 'sidebar', 'asymmetric', 'minimal']
    
    LAYOUT_RULES = {
        'movie': {'layouts': ['hero', 'split', 'grid'], 'text_align': ['center', 'left'], 'colors': ['#1a1a2e', '#faefcf']},
        'music': {'layouts': ['asymmetric', 'sidebar', 'hero'], 'text_align': ['left', 'right'], 'colors': ['#0f0f23', '#ff6b6b']},
        'event': {'layouts': ['split', 'minimal', 'grid'], 'text_align': ['center', 'left'], 'colors': ['#fff4e1', '#ffd700']},
        'sports': {'layouts': ['hero', 'asymmetric', 'split'], 'text_align': ['left', 'center'], 'colors': ['#000000', '#ff4444']},
    }
    
    def generate(self, genre: str = 'movie') -> Dict:
        """Generate template with random layout and alignment"""
        w, h = 720, 1080
        rules = self.LAYOUT_RULES.get(genre, self.LAYOUT_RULES['movie'])
        
        layout_type = random.choice(rules['layouts'])
        text_align = random.choice(rules['text_align'])
        bg_color = random.choice(rules['colors'])
        
        layout_func = getattr(self, f'_{layout_type}_layout')
        template = layout_func(w, h)
        
        template['genre'] = genre
        template['layout_type'] = layout_type
        template['background_color'] = bg_color
        template['fonts'] = {
            'title': {'family': 'Graduate-Regular.ttf', 'size': 42, 'color': '#043bb4', 'align': text_align},
            'caption': {'family': 'Graduate-Regular.ttf', 'size': 18, 'color': '#043bb4', 'align': text_align}
        }
        
        return template
    
    def _split_layout(self, w, h):
        mid = h // 2
        margin = 40
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin, w - margin, mid - 20]},
                {'name': 'Text', 'bbox': [margin * 2, mid + 40, w - margin * 2, mid + 100]},
                {'name': 'Caption', 'bbox': [margin * 2, mid + 120, w - margin * 2, h - margin]}
            ]
        }
    
    def _grid_layout(self, w, h):
        margin = 50
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin * 2, w - margin, h - 200]},
                {'name': 'Text', 'bbox': [margin * 2, h - 180, w - margin * 2, h - 120]},
                {'name': 'Caption', 'bbox': [margin * 2, h - 100, w - margin * 2, h - margin]}
            ]
        }
    
    def _hero_layout(self, w, h):
        margin = 30
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin, w - margin, h - 250]},
                {'name': 'Text', 'bbox': [margin * 2, h - 220, w - margin * 2, h - 150]},
                {'name': 'Caption', 'bbox': [margin * 2, h - 130, w - margin * 2, h - margin * 2]}
            ]
        }
    
    def _sidebar_layout(self, w, h):
        split = int(w * 0.6)
        margin = 40
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin, split - 20, h - margin]},
                {'name': 'Text', 'bbox': [split + 20, h // 3, w - margin, h // 3 + 80]},
                {'name': 'Caption', 'bbox': [split + 20, h // 3 + 100, w - margin, h - margin]}
            ]
        }
    
    def _asymmetric_layout(self, w, h):
        margin = 35
        offset = 80
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [offset, margin, w - margin, h - 280]},
                {'name': 'Text', 'bbox': [margin, h - 250, w - offset, h - 180]},
                {'name': 'Caption', 'bbox': [margin, h - 160, w - offset, h - margin * 2]}
            ]
        }
    
    def _minimal_layout(self, w, h):
        margin = 80
        return {
            'size': [w, h],
            'layers': [
                {'name': 'Background', 'bbox': [0, 0, w, h]},
                {'name': 'Image', 'bbox': [margin, margin * 2, w - margin, h - 300]},
                {'name': 'Text', 'bbox': [margin * 2, h - 250, w - margin * 2, h - 180]},
                {'name': 'Caption', 'bbox': [margin * 2, h - 160, w - margin * 2, h - margin * 2]}
            ]
        }
