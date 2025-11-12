"""Add styled movie title to poster"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

class TextOverlay:
    def __init__(self):
        pass
    
    def add_title(self, image, title, style="cinematic"):
        """Add styled title to poster"""
        img = image.copy()
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Try to load font, fallback to default
        try:
            if style == "cinematic":
                font_size = int(height * 0.08)
                font = ImageFont.truetype("arial.ttf", font_size)
            elif style == "bold":
                font_size = int(height * 0.1)
                font = ImageFont.truetype("arialbd.ttf", font_size)
            else:
                font_size = int(height * 0.08)
                font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Position at bottom
        title_upper = title.upper()
        bbox = draw.textbbox((0, 0), title_upper, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - int(height * 0.05)
        
        # Add shadow for readability
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), title_upper, font=font, fill=(0, 0, 0, 200))
        
        # Add main text
        draw.text((x, y), title_upper, font=font, fill=(255, 255, 255, 255))
        
        return img
