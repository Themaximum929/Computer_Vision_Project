"""Template Engine - Professional poster layouts"""
from PIL import Image, ImageDraw, ImageFont
import json

class TemplateEngine:
    def __init__(self):
        self.templates = {
            'minimal': {
                'title_position': 'bottom',
                'title_align': 'center',
                'title_size_ratio': 0.08,
                'margins': (50, 50, 50, 150),
                'overlay': None,
                'border': False
            },
            'bold': {
                'title_position': 'top',
                'title_align': 'left',
                'title_size_ratio': 0.12,
                'margins': (60, 80, 60, 60),
                'overlay': 'gradient_bottom',
                'border': False
            },
            'vintage': {
                'title_position': 'center',
                'title_align': 'center',
                'title_size_ratio': 0.10,
                'margins': (80, 80, 80, 80),
                'overlay': 'vignette',
                'border': True,
                'border_width': 20
            },
            'modern': {
                'title_position': 'bottom_left',
                'title_align': 'left',
                'title_size_ratio': 0.09,
                'margins': (60, 60, 60, 100),
                'overlay': 'accent_bar',
                'border': False
            },
            'cinematic': {
                'title_position': 'center',
                'title_align': 'center',
                'title_size_ratio': 0.11,
                'margins': (40, 200, 40, 200),
                'overlay': 'letterbox',
                'border': False
            }
        }
    
    def get_template(self, name):
        """Get template configuration"""
        return self.templates.get(name, self.templates['minimal'])
    
    def apply_overlay(self, image, overlay_type, color=(0, 0, 0)):
        """Apply overlay effects"""
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        width, height = image.size
        
        if overlay_type == 'gradient_bottom':
            for y in range(height // 2, height):
                alpha = int(255 * (y - height // 2) / (height // 2))
                draw.rectangle([(0, y), (width, y+1)], fill=(*color, alpha))
        
        elif overlay_type == 'vignette':
            for i in range(100):
                alpha = int(i * 2.55)
                inset = int(i * min(width, height) / 200)
                draw.rectangle(
                    [(inset, inset), (width-inset, height-inset)],
                    outline=(*color, alpha),
                    width=2
                )
        
        elif overlay_type == 'letterbox':
            bar_height = height // 6
            draw.rectangle([(0, 0), (width, bar_height)], fill=(*color, 200))
            draw.rectangle([(0, height-bar_height), (width, height)], fill=(*color, 200))
        
        elif overlay_type == 'accent_bar':
            bar_width = 10
            draw.rectangle([(0, 0), (bar_width, height)], fill=(*color, 255))
        
        return Image.alpha_composite(image.convert('RGBA'), overlay)
    
    def add_border(self, image, width=20, color=(255, 255, 255)):
        """Add border to image"""
        bordered = Image.new('RGB', 
                            (image.width + width*2, image.height + width*2),
                            color)
        bordered.paste(image, (width, width))
        return bordered
    
    def calculate_title_position(self, image_size, template, text_size):
        """Calculate optimal title position based on template"""
        width, height = image_size
        text_width, text_height = text_size
        margins = template['margins']
        
        positions = {
            'top': (width // 2, margins[1]),
            'center': (width // 2, height // 2),
            'bottom': (width // 2, height - margins[3]),
            'bottom_left': (margins[0], height - margins[3]),
            'top_left': (margins[0], margins[1])
        }
        
        return positions.get(template['title_position'], positions['bottom'])
