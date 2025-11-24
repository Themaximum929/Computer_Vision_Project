"""Modern PIL Text Overlay with Advanced Effects"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

class ModernTextOverlay:
    """PIL-based text with glow, gradients, and smart positioning"""
    
    def __init__(self):
        self.font_pools = {
            'action': ['BebasNeueRegular.ttf', 'Arvo-Bold.ttf', 'Hexaplex.otf'],
            'horror': ['TrajanPro-Regular.ttf', 'bodoni_[allfont.net].ttf'],
            'scifi': ['Blocksmith.otf', 'Hexaplex.otf', 'ShinkosansRegular-8OO50.otf'],
            'romance': ['PlayfairDisplay-Regular.ttf', 'CinzelDecorative-Regular.ttf'],
            'comedy': ['Lobster-Regular.ttf', 'Waffle Mango.ttf'],
            'fantasy': ['CinzelDecorative-Bold.ttf', 'TrajanPro-Regular.ttf'],
            'thriller': ['Arvo-Bold.ttf', 'BebasNeueRegular.ttf'],
            'drama': ['bodoni_[allfont.net].ttf', 'PlayfairDisplay-Regular.ttf']
        }
    
    def add_text(self, image, title, genre='action'):
        """Add text with modern effects"""
        w, h = image.size
        
        # Get font
        fonts = self.font_pools.get(genre, self.font_pools['action'])
        font_name = fonts[0]
        font_size = int(h * 0.12)
        
        try:
            font = ImageFont.truetype(f'fonts/cinematic/{font_name}', font_size)
        except:
            font = ImageFont.load_default()
        
        # Find best position (bottom third, centered)
        y_pos = int(h * 0.80)
        
        # Genre-specific colors and effects
        if genre == 'scifi':
            return self._add_glow_text(image, title, font, y_pos, 
                                      color=(0, 200, 255), glow_color=(0, 100, 255, 180))
        elif genre == 'horror':
            return self._add_shadow_text(image, title, font, y_pos,
                                        color=(200, 0, 0), shadow_color=(50, 0, 0))
        elif genre == 'fantasy':
            return self._add_glow_text(image, title, font, y_pos,
                                      color=(255, 215, 0), glow_color=(255, 140, 0, 180))
        else:
            return self._add_glow_text(image, title, font, y_pos,
                                      color=(255, 255, 255), glow_color=(255, 255, 255, 150))
    
    def _add_glow_text(self, image, text, font, y_pos, color, glow_color):
        """Add text with glow effect"""
        w, h = image.size
        
        # Create text layer
        txt_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x_pos = (w - text_w) // 2
        
        # Draw glow (multiple blurred layers)
        glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        for i in range(5):
            offset = i * 2
            glow_draw.text((x_pos + offset, y_pos + offset), text, font=font, fill=glow_color)
            glow_draw.text((x_pos - offset, y_pos - offset), text, font=font, fill=glow_color)
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(10))
        
        # Composite glow
        result = Image.alpha_composite(image.convert('RGBA'), glow_layer)
        
        # Draw main text with outline
        draw = ImageDraw.Draw(result)
        for ox, oy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
            draw.text((x_pos+ox, y_pos+oy), text, font=font, fill=(0, 0, 0, 255))
        draw.text((x_pos, y_pos), text, font=font, fill=color)
        
        return result.convert('RGB')
    
    def _add_shadow_text(self, image, text, font, y_pos, color, shadow_color):
        """Add text with dramatic shadow"""
        w, h = image.size
        
        txt_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x_pos = (w - text_w) // 2
        
        # Large shadow
        for i in range(10, 0, -1):
            alpha = int(100 * (i / 10))
            draw.text((x_pos + i*2, y_pos + i*2), text, font=font, 
                     fill=(*shadow_color, alpha))
        
        # Main text
        draw.text((x_pos, y_pos), text, font=font, fill=color)
        
        return Image.alpha_composite(image.convert('RGBA'), txt_layer).convert('RGB')
