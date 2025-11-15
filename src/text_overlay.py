"""Add styled movie title to poster"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from src.poster_text_styles import POSTER_STYLES

class TextOverlay:
    def __init__(self):
        self.styles = POSTER_STYLES
    
    def add_title(self, image, title, style="cinematic", genre=None):
        """Add styled title to poster with genre-specific styling"""
        # Use genre style if provided, otherwise use specified style
        if genre and genre.lower() in self.styles:
            style_config = self.styles[genre.lower()]
        elif style in self.styles:
            style_config = self.styles[style]
        else:
            style_config = self.styles["cinematic"]
        
        img = image.copy()
        width, height = img.size
        
        # Load font
        font_size = int(height * style_config["size_ratio"])
        font = self._load_font(style_config["font"], style_config["fallback"], font_size)
        
        # Prepare title
        title_upper = title.upper()
        
        # Create text with letter spacing
        spaced_title = self._add_letter_spacing(title_upper, style_config["letter_spacing"])
        
        # Calculate position
        x, y = self._calculate_position(img, spaced_title, font, style_config["position"])
        
        # Draw text with effects
        img = self._draw_text_with_effects(img, spaced_title, font, x, y, style_config)
        
        return img
    
    def _load_font(self, font_name, fallback_name, size):
        """Load font with fallback"""
        try:
            return ImageFont.truetype(font_name, size)
        except:
            try:
                return ImageFont.truetype(fallback_name, size)
            except:
                return ImageFont.load_default()
    
    def _add_letter_spacing(self, text, spacing):
        """Add letter spacing to text"""
        if spacing <= 0:
            return text
        return ' '.join(text)
    
    def _calculate_position(self, image, text, font, position):
        """Calculate text position"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        
        if position == "top":
            y = int(height * 0.05)
        elif position == "center":
            y = (height - text_height) // 2
        else:  # bottom
            y = height - text_height - int(height * 0.08)
        
        return x, y
    
    def _draw_text_with_effects(self, image, text, font, x, y, style_config):
        """Draw text with shadow, stroke, and color effects"""
        # Create a transparent overlay for better blending
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw shadow
        shadow_offset = style_config["shadow_offset"]
        shadow_color = style_config["shadow_color"]
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Draw stroke (outline)
        if style_config["stroke_width"] > 0:
            stroke_width = style_config["stroke_width"]
            stroke_color = style_config["stroke_color"]
            draw.text((x, y), text, font=font, fill=stroke_color, stroke_width=stroke_width, stroke_fill=stroke_color)
        
        # Draw main text
        text_color = style_config["color"]
        draw.text((x, y), text, font=font, fill=text_color)
        
        # Composite overlay onto image
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay)
        image = image.convert('RGB')
        
        return image
