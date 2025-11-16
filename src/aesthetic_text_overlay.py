"""Aesthetic Text Overlay - PosterCraft Style"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

class AestheticTextOverlay:
    """Professional text overlay with gradient backgrounds and hierarchy"""
    
    def __init__(self):
        # Genre-specific font combinations
        self.genre_fonts = {
            "action": {
                "title": "fonts/cinematic/BebasNeueRegular.ttf",
                "tagline": "fonts/cinematic/Montserrat-Bold.ttf"
            },
            "horror": {
                "title": "fonts/cinematic/TrajanPro-Regular.ttf",
                "tagline": "fonts/cinematic/garamond_[allfont.ru].ttf"
            },
            "scifi": {
                "title": "fonts/cinematic/Blocksmith.otf",
                "tagline": "fonts/cinematic/GothamRegular-1GwDg.ttf"
            },
            "romance": {
                "title": "fonts/cinematic/PlayfairDisplay-Regular.ttf",
                "tagline": "fonts/cinematic/Montserrat-Regular.ttf"
            },
            "comedy": {
                "title": "fonts/cinematic/Lobster-Regular.ttf",
                "tagline": "fonts/cinematic/Montserrat-Regular.ttf"
            },
            "fantasy": {
                "title": "fonts/cinematic/CinzelDecorative-Bold.ttf",
                "tagline": "fonts/cinematic/garamond_[allfont.ru].ttf"
            },
            "thriller": {
                "title": "fonts/cinematic/Arvo-Bold.ttf",
                "tagline": "fonts/cinematic/Montserrat-Regular.ttf"
            },
            "drama": {
                "title": "fonts/cinematic/bodoni_[allfont.net].ttf",
                "tagline": "fonts/cinematic/garamond_[allfont.ru].ttf"
            },
        }
        self.default_fonts = {
            "title": "fonts/cinematic/BebasNeueRegular.ttf",
            "tagline": "fonts/cinematic/Montserrat-Regular.ttf"
        }
    
    def add_poster_text(self, image, title, genre="cinematic", tagline=None, credits=None):
        """Add complete text overlay with gradient background"""
        w, h = image.size
        
        # Step 1: Add gradient overlay
        image = self._add_gradient_overlay(image, genre)
        
        # Step 2: Add title
        image = self._add_title(image, title, genre)
        
        # Step 3: Add tagline (optional)
        if tagline:
            image = self._add_tagline(image, tagline, genre)
        
        # Step 4: Add credits (optional)
        if credits:
            image = self._add_credits(image, credits)
        
        return image
    
    def _add_gradient_overlay(self, image, genre):
        """Add gradient overlay for text readability"""
        w, h = image.size
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Genre-specific gradient
        if genre in ["horror", "thriller"]:
            # Strong dark gradient
            for i in range(int(h * 0.4)):
                alpha = int(200 * (i / (h * 0.4)))
                draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
        elif genre in ["romance", "comedy"]:
            # Soft gradient
            for i in range(int(h * 0.3)):
                alpha = int(120 * (i / (h * 0.3)))
                draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
        else:
            # Standard gradient
            for i in range(int(h * 0.35)):
                alpha = int(160 * (i / (h * 0.35)))
                draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
        
        return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    
    def _add_title(self, image, title, genre):
        """Add main title with professional styling"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        # Load genre-specific font
        fonts = self.genre_fonts.get(genre, self.default_fonts)
        try:
            font_size = int(h * 0.1)
            font = ImageFont.truetype(fonts["title"], font_size)
        except:
            try:
                font = ImageFont.truetype(self.default_fonts["title"], font_size)
            except:
                font = ImageFont.load_default()
        
        # Genre-specific colors
        colors = {
            "action": (255, 50, 50),
            "horror": (200, 0, 0),
            "scifi": (0, 200, 255),
            "romance": (255, 150, 200),
            "comedy": (255, 220, 0),
            "fantasy": (255, 215, 0),
        }
        text_color = colors.get(genre, (255, 255, 255))
        
        # Position
        title_upper = title.upper()
        bbox = draw.textbbox((0, 0), title_upper, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        y = int(h * 0.82)
        
        # Draw with shadow and outline
        # Shadow
        shadow_offset = int(font_size * 0.03)
        draw.text((x + shadow_offset, y + shadow_offset), title_upper, 
                 font=font, fill=(0, 0, 0, 180))
        
        # Outline
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            draw.text((x + offset[0], y + offset[1]), title_upper, 
                     font=font, fill=(0, 0, 0))
        
        # Main text
        draw.text((x, y), title_upper, font=font, fill=text_color)
        
        return image
    
    def _add_tagline(self, image, tagline, genre="cinematic"):
        """Add tagline above title"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        # Load genre-specific font
        fonts = self.genre_fonts.get(genre, self.default_fonts)
        try:
            font_size = int(h * 0.025)
            font = ImageFont.truetype(fonts["tagline"], font_size)
        except:
            try:
                font = ImageFont.truetype(self.default_fonts["tagline"], font_size)
            except:
                font = ImageFont.load_default()
        
        # Position above title
        bbox = draw.textbbox((0, 0), tagline, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        y = int(h * 0.76)
        
        # Draw with subtle shadow
        draw.text((x + 1, y + 1), tagline, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), tagline, font=font, fill=(200, 200, 200))
        
        return image
    
    def _add_credits(self, image, credits):
        """Add credits at bottom"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.018)
            font = ImageFont.truetype(self.font_paths["tagline"], font_size)
        except:
            font = ImageFont.load_default()
        
        # Position at bottom
        bbox = draw.textbbox((0, 0), credits, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        y = int(h * 0.94)
        
        draw.text((x, y), credits, font=font, fill=(180, 180, 180))
        
        return image
    
    def add_minimal_text(self, image, title, accent_color=None):
        """Minimal text overlay for modern designs"""
        w, h = image.size
        
        # Subtle gradient
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        for i in range(int(h * 0.25)):
            alpha = int(100 * (i / (h * 0.25)))
            draw_overlay.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
        
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Add title
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.08)
            font = ImageFont.truetype(self.font_paths["title"], font_size)
        except:
            font = ImageFont.load_default()
        
        title_upper = title.upper()
        bbox = draw.textbbox((0, 0), title_upper, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        y = int(h * 0.85)
        
        # Use accent color if provided
        text_color = accent_color if accent_color else (255, 255, 255)
        
        # Simple shadow
        draw.text((x + 2, y + 2), title_upper, font=font, fill=(0, 0, 0))
        draw.text((x, y), title_upper, font=font, fill=text_color)
        
        return image
