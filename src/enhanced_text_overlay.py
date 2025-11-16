"""Enhanced Text Overlay - Dynamic fonts, positioning, and styling"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

class EnhancedTextOverlay:
    """Dynamic text overlay with font pools, flexible positioning, and variations"""
    
    def __init__(self):
        self._init_font_pools()
        self._init_positioning_rules()
    
    def _init_font_pools(self):
        """3-5 cinematic fonts per genre"""
        self.font_pools = {
            'action': {
                'title': ['BebasNeueRegular.ttf', 'Arvo-Bold.ttf', 'Hexaplex.otf', 'Street-Robot-Slab.ttf'],
                'tagline': ['Montserrat-Bold.ttf', 'GothamRegular-1GwDg.ttf', 'Arvo-Bold.ttf'],
                'credits': ['Montserrat-Regular.ttf', 'GothamRegular-1GwDg.ttf']
            },
            'horror': {
                'title': ['TrajanPro-Regular.ttf', 'bodoni_[allfont.net].ttf', 'CinzelDecorative-Bold.ttf'],
                'tagline': ['garamond_[allfont.ru].ttf', 'PlayfairDisplay-Regular.ttf'],
                'credits': ['garamond_[allfont.ru].ttf', 'Montserrat-Regular.ttf']
            },
            'scifi': {
                'title': ['Blocksmith.otf', 'Hexaplex.otf', 'ShinkosansRegular-8OO50.otf', 'Redhawk.otf'],
                'tagline': ['GothamRegular-1GwDg.ttf', 'Montserrat-Regular.ttf'],
                'credits': ['GothamRegular-1GwDg.ttf', 'Montserrat-Regular.ttf']
            },
            'romance': {
                'title': ['PlayfairDisplay-Regular.ttf', 'CinzelDecorative-Regular.ttf', 'Finlikless-Regular.ttf'],
                'tagline': ['Montserrat-Regular.ttf', 'garamond_[allfont.ru].ttf'],
                'credits': ['Montserrat-Regular.ttf']
            },
            'comedy': {
                'title': ['Lobster-Regular.ttf', 'Waffle Mango.ttf', 'VTKS LOVEANDPEACE.ttf'],
                'tagline': ['Montserrat-Regular.ttf', 'Handvetica Neue Regular Trial.ttf'],
                'credits': ['Montserrat-Regular.ttf']
            },
            'fantasy': {
                'title': ['CinzelDecorative-Bold.ttf', 'TrajanPro-Regular.ttf', 'Alkia.ttf', 'Divergentes-zrd2a.ttf'],
                'tagline': ['garamond_[allfont.ru].ttf', 'CinzelDecorative-Regular.ttf'],
                'credits': ['garamond_[allfont.ru].ttf']
            },
            'thriller': {
                'title': ['Arvo-Bold.ttf', 'BebasNeueRegular.ttf', 'Plateaux (2).ttf'],
                'tagline': ['Montserrat-Regular.ttf', 'GothamRegular-1GwDg.ttf'],
                'credits': ['Montserrat-Regular.ttf']
            },
            'drama': {
                'title': ['bodoni_[allfont.net].ttf', 'PlayfairDisplay-Regular.ttf', 'TrajanPro-Regular.ttf'],
                'tagline': ['garamond_[allfont.ru].ttf', 'Montserrat-Regular.ttf'],
                'credits': ['garamond_[allfont.ru].ttf']
            }
        }
    
    def _init_positioning_rules(self):
        """Flexible vertical positioning with randomization"""
        self.positioning_rules = {
            'action': {'base_y': 0.80, 'variance': 0.05, 'align_pool': ['center', 'left']},
            'horror': {'base_y': 0.82, 'variance': 0.03, 'align_pool': ['center']},
            'scifi': {'base_y': 0.78, 'variance': 0.06, 'align_pool': ['center', 'right']},
            'romance': {'base_y': 0.85, 'variance': 0.04, 'align_pool': ['center']},
            'comedy': {'base_y': 0.75, 'variance': 0.08, 'align_pool': ['center', 'left']},
            'fantasy': {'base_y': 0.83, 'variance': 0.04, 'align_pool': ['center']},
            'thriller': {'base_y': 0.79, 'variance': 0.05, 'align_pool': ['left', 'center']},
            'drama': {'base_y': 0.84, 'variance': 0.03, 'align_pool': ['center']}
        }
    
    def add_poster_text(self, image, title, genre='action', tagline=None, credits=None):
        """Add text with dynamic fonts and positioning"""
        w, h = image.size
        margin = int(w * 0.05)
        
        # Random font selection
        fonts = self.font_pools.get(genre, self.font_pools['action'])
        title_font_name = random.choice(fonts['title'])
        tagline_font_name = random.choice(fonts['tagline'])
        credits_font_name = random.choice(fonts['credits'])
        
        # Positioning rules
        rules = self.positioning_rules.get(genre, self.positioning_rules['action'])
        base_y = rules['base_y']
        variance = rules['variance']
        align = random.choice(rules['align_pool'])
        
        # Random vertical shift
        y_shift = random.uniform(-variance, variance)
        title_y = base_y + y_shift
        
        # Gradient overlay
        image = self._add_gradient(image, title_y)
        
        # Add title
        image = self._add_title(image, title, genre, title_font_name, title_y, align, margin)
        
        # Add tagline
        if tagline:
            tagline_y = title_y - 0.06
            image = self._add_tagline(image, tagline, tagline_font_name, tagline_y, align, margin)
        
        # Add credits
        if credits:
            image = self._add_credits(image, credits, credits_font_name, margin)
        
        return image
    
    def _add_gradient(self, image, title_y):
        """Adaptive gradient based on title position"""
        w, h = image.size
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        gradient_range = int(h * 0.4)
        start_y = int(h * title_y) - gradient_range // 2
        
        for i in range(gradient_range):
            alpha = int(160 * (i / gradient_range))
            y = max(0, min(h - 1, start_y + i))
            draw.rectangle([(0, y), (w, y + 1)], fill=(0, 0, 0, alpha))
        
        return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    
    def _add_title(self, image, title, genre, font_name, y_ratio, align, margin):
        """Add title with rotation, shadows, and gradient fill"""
        w, h = image.size
        
        # Load font
        try:
            font_size = int(h * 0.12)
            font = ImageFont.truetype(f'fonts/cinematic/{font_name}', font_size)
        except:
            font = ImageFont.load_default()
        
        # Create text layer
        text_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Measure text
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Auto-size if too wide
        while text_w > w - 2 * margin and font_size > 30:
            font_size -= 2
            try:
                font = ImageFont.truetype(f'fonts/cinematic/{font_name}', font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), title, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        
        # Position based on alignment
        if align == 'center':
            x = (w - text_w) // 2
        elif align == 'left':
            x = margin
        else:  # right
            x = w - text_w - margin
        
        # Clamp position
        x = max(margin, min(x, w - text_w - margin))
        y = int(h * y_ratio)
        y = max(margin, min(y, h - text_h - margin))
        
        # Genre colors
        colors = {
            'action': (255, 50, 50),
            'horror': (200, 0, 0),
            'scifi': (0, 200, 255),
            'romance': (255, 150, 200),
            'comedy': (255, 220, 0),
            'fantasy': (255, 215, 0),
            'thriller': (180, 180, 255),
            'drama': (220, 220, 220)
        }
        text_color = colors.get(genre, (255, 255, 255))
        
        # Multi-layer shadows with varied opacity
        for i in range(3):
            offset = (i + 1) * 2
            alpha = 200 - i * 50
            shadow_x = min(x + offset, w - text_w - margin)
            shadow_y = min(y + offset, h - text_h - margin)
            draw.text((shadow_x, shadow_y), title, font=font, fill=(0, 0, 0, alpha))
        
        # Outline
        for ox, oy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            draw.text((x+ox, y+oy), title, font=font, fill=(0, 0, 0, 255))
        
        # Main text
        draw.text((x, y), title, font=font, fill=text_color)
        
        return Image.alpha_composite(image.convert('RGBA'), text_layer).convert('RGB')
    
    def _add_tagline(self, image, tagline, font_name, y_ratio, align, margin):
        """Add tagline with wrapping support"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.025)
            font = ImageFont.truetype(f'fonts/cinematic/{font_name}', font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text if needed
        max_width = w - 2 * margin
        words = tagline.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        y = int(h * y_ratio)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            if align == 'center':
                x = (w - text_w) // 2
            elif align == 'left':
                x = margin
            else:
                x = w - text_w - margin
            
            x = max(margin, min(x, w - text_w - margin))
            y = max(margin, min(y, h - text_h - margin))
            
            # Shadow
            draw.text((x + 1, y + 1), line, font=font, fill=(0, 0, 0, 150))
            draw.text((x, y), line, font=font, fill=(200, 200, 200))
            
            y += text_h + 5
        
        return image
    
    def _add_credits(self, image, credits, font_name, margin):
        """Add credits at bottom"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.018)
            font = ImageFont.truetype(f'fonts/cinematic/{font_name}', font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), credits, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (w - text_w) // 2
        x = max(margin, min(x, w - text_w - margin))
        y = h - text_h - margin
        
        draw.text((x, y), credits, font=font, fill=(180, 180, 180))
        return image
