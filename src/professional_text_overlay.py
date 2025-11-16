"""Professional Text Overlay - Commercial Grade with PosterCraft Features"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import numpy as np
from sklearn.cluster import KMeans
import colorsys
import random
import math

class ProfessionalTextOverlay:
    """Commercial-grade text overlay with layouts, moods, and background-aware colors"""
    
    def __init__(self, use_llm_titles=False):
        self._init_layouts()
        self._init_typography()
        self._init_moods()
        self._init_effects()
        self.use_llm_titles = use_llm_titles
    
    def _init_layouts(self):
        """Define multiple layout archetypes per genre"""
        self.layouts = {
            'centered': {'title_y': 0.82, 'tagline_y': 0.76, 'align': 'center', 'rotation': 0},
            'top_heavy': {'title_y': 0.15, 'tagline_y': 0.22, 'align': 'center', 'rotation': 0},
            'asymmetric_left': {'title_y': 0.80, 'tagline_y': 0.75, 'align': 'left', 'rotation': 0},
            'asymmetric_right': {'title_y': 0.80, 'tagline_y': 0.75, 'align': 'right', 'rotation': 0},
            'festival': {'title_y': 0.12, 'tagline_y': 0.88, 'align': 'center', 'rotation': 0},
            'hero': {'title_y': 0.85, 'tagline_y': 0.78, 'align': 'center', 'rotation': 0},
            'split': {'title_y': 0.50, 'tagline_y': 0.58, 'align': 'center', 'rotation': 0},
            'tilted': {'title_y': 0.82, 'tagline_y': 0.76, 'align': 'center', 'rotation': -5}
        }
        
        # Genre-preferred layouts
        self.genre_layouts = {
            'action': ['hero', 'tilted', 'asymmetric_left'],
            'horror': ['centered', 'top_heavy', 'festival'],
            'scifi': ['asymmetric_right', 'split', 'centered'],
            'romance': ['centered', 'festival', 'hero'],
            'comedy': ['tilted', 'asymmetric_left', 'hero'],
            'fantasy': ['festival', 'centered', 'hero'],
            'thriller': ['asymmetric_left', 'top_heavy', 'centered'],
            'drama': ['centered', 'festival', 'split']
        }
    
    def _init_typography(self):
        """Rich typography system with multiple roles and variants"""
        self.typography = {
            'action': {
                'variants': [
                    {'title': 'fonts/cinematic/BebasNeueRegular.ttf', 'weight': 'bold', 'caps': True},
                    {'title': 'fonts/cinematic/Arvo-Bold.ttf', 'weight': 'bold', 'caps': True}
                ],
                'tagline': 'fonts/cinematic/Montserrat-Bold.ttf',
                'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
                'tracking': 'normal'
            },
            'horror': {
                'variants': [
                    {'title': 'fonts/cinematic/TrajanPro-Regular.ttf', 'weight': 'regular', 'caps': False},
                    {'title': 'fonts/cinematic/bodoni_[allfont.net].ttf', 'weight': 'regular', 'caps': False}
                ],
                'tagline': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'credits': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'tracking': 'tight'
            },
            'scifi': {
                'variants': [
                    {'title': 'fonts/cinematic/Blocksmith.otf', 'weight': 'bold', 'caps': True},
                    {'title': 'fonts/cinematic/GothamRegular-1GwDg.ttf', 'weight': 'bold', 'caps': True}
                ],
                'tagline': 'fonts/cinematic/GothamRegular-1GwDg.ttf',
                'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
                'tracking': 'wide'
            },
            'romance': {
                'variants': [
                    {'title': 'fonts/cinematic/PlayfairDisplay-Regular.ttf', 'weight': 'regular', 'caps': False},
                    {'title': 'fonts/cinematic/CinzelDecorative-Bold.ttf', 'weight': 'regular', 'caps': False}
                ],
                'tagline': 'fonts/cinematic/Montserrat-Regular.ttf',
                'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
                'tracking': 'wide'
            },
            'comedy': {
                'variants': [
                    {'title': 'fonts/cinematic/Lobster-Regular.ttf', 'weight': 'regular', 'caps': False}
                ],
                'tagline': 'fonts/cinematic/Montserrat-Regular.ttf',
                'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
                'tracking': 'normal'
            },
            'fantasy': {
                'variants': [
                    {'title': 'fonts/cinematic/CinzelDecorative-Bold.ttf', 'weight': 'bold', 'caps': False},
                    {'title': 'fonts/cinematic/TrajanPro-Regular.ttf', 'weight': 'regular', 'caps': False}
                ],
                'tagline': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'credits': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'tracking': 'normal'
            },
            'thriller': {
                'variants': [
                    {'title': 'fonts/cinematic/Arvo-Bold.ttf', 'weight': 'bold', 'caps': True}
                ],
                'tagline': 'fonts/cinematic/Montserrat-Regular.ttf',
                'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
                'tracking': 'tight'
            },
            'drama': {
                'variants': [
                    {'title': 'fonts/cinematic/bodoni_[allfont.net].ttf', 'weight': 'regular', 'caps': False},
                    {'title': 'fonts/cinematic/PlayfairDisplay-Regular.ttf', 'weight': 'regular', 'caps': False}
                ],
                'tagline': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'credits': 'fonts/cinematic/garamond_[allfont.ru].ttf',
                'tracking': 'normal'
            }
        }
        
        self.default_typography = {
            'variants': [{'title': 'fonts/cinematic/BebasNeueRegular.ttf', 'weight': 'bold', 'caps': True}],
            'tagline': 'fonts/cinematic/Montserrat-Regular.ttf',
            'credits': 'fonts/cinematic/Montserrat-Regular.ttf',
            'tracking': 'normal'
        }
    
    def _init_moods(self):
        """Mood-driven style parameters"""
        self.moods = {
            'noir': {'gradient_strength': 0.8, 'saturation': 0.3, 'glow_intensity': 0.2},
            'minimalist': {'gradient_strength': 0.3, 'saturation': 0.5, 'glow_intensity': 0.1},
            'vintage': {'gradient_strength': 0.5, 'saturation': 0.6, 'glow_intensity': 0.3},
            'energetic': {'gradient_strength': 0.6, 'saturation': 1.0, 'glow_intensity': 0.8},
            'surreal': {'gradient_strength': 0.4, 'saturation': 0.9, 'glow_intensity': 0.6},
            'corporate': {'gradient_strength': 0.4, 'saturation': 0.4, 'glow_intensity': 0.2},
            'epic': {'gradient_strength': 0.7, 'saturation': 0.8, 'glow_intensity': 0.5}
        }
    
    def _init_effects(self):
        """Multi-layer effect configurations"""
        self.effects = {
            'action': {'shadow_layers': 2, 'glow': True, 'gradient_fill': False},
            'horror': {'shadow_layers': 3, 'glow': True, 'gradient_fill': False},
            'scifi': {'shadow_layers': 1, 'glow': True, 'gradient_fill': True},
            'romance': {'shadow_layers': 1, 'glow': True, 'gradient_fill': True},
            'comedy': {'shadow_layers': 1, 'glow': False, 'gradient_fill': False},
            'fantasy': {'shadow_layers': 2, 'glow': True, 'gradient_fill': True},
            'thriller': {'shadow_layers': 2, 'glow': True, 'gradient_fill': False},
            'drama': {'shadow_layers': 1, 'glow': False, 'gradient_fill': False}
        }
    
    def add_poster_text(self, image, title, genre='action', tagline=None, credits=None, 
                       layout=None, mood='epic', variant_seed=None):
        """Add professional text with all enhancements"""
        if variant_seed is not None:
            random.seed(variant_seed)
        
        # Generate single-word title using AI
        from src.title_generator import TitleGenerator
        title_gen = TitleGenerator(use_llm=self.use_llm_titles)
        title = title_gen.generate(title, genre)
        
        # Select layout
        if layout is None:
            layout = random.choice(self.genre_layouts.get(genre, ['centered']))
        layout_config = self.layouts[layout]
        
        # Get mood parameters
        mood_params = self.moods.get(mood, self.moods['epic'])
        
        # Extract background colors
        bg_colors = self._extract_background_colors(image, layout_config)
        
        # Select typography variant
        typo = self.typography.get(genre, self.default_typography)
        title_variant = random.choice(typo['variants'])
        
        # Apply gradient overlay
        image = self._add_adaptive_gradient(image, genre, mood_params, layout_config)
        
        # Get smart text color
        text_color = self._get_smart_text_color(bg_colors, genre, mood_params)
        
        # Add title with effects
        image = self._add_enhanced_title(
            image, title, genre, layout_config, title_variant, 
            text_color, mood_params
        )
        
        # Add tagline
        if tagline:
            image = self._add_enhanced_tagline(
                image, tagline, genre, layout_config, typo, 
                text_color, mood_params
            )
        
        # Add credits
        if credits:
            image = self._add_credits(image, credits, typo, layout_config)
        
        return image
    
    def _extract_background_colors(self, image, layout_config):
        """Sample dominant colors from text region"""
        w, h = image.size
        y_pos = int(h * layout_config['title_y'])
        
        # Sample region around text
        region_height = int(h * 0.2)
        y_start = max(0, y_pos - region_height // 2)
        y_end = min(h, y_pos + region_height // 2)
        
        region = image.crop((0, y_start, w, y_end))
        pixels = np.array(region.resize((50, 50))).reshape(-1, 3)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        return [tuple(map(int, color)) for color in kmeans.cluster_centers_]
    
    def _get_smart_text_color(self, bg_colors, genre, mood_params):
        """Background-aware color selection with contrast check"""
        # Calculate average luminance
        avg_lum = sum(0.299*r + 0.587*g + 0.114*b for r,g,b in bg_colors) / (3 * 255)
        
        # Genre base colors
        genre_colors = {
            'action': (255, 50, 50),
            'horror': (200, 0, 0),
            'scifi': (0, 200, 255),
            'romance': (255, 150, 200),
            'comedy': (255, 220, 0),
            'fantasy': (255, 215, 0),
            'thriller': (180, 180, 255),
            'drama': (220, 220, 220)
        }
        
        base_color = genre_colors.get(genre, (255, 255, 255))
        
        # Adjust saturation based on mood
        h, s, v = colorsys.rgb_to_hsv(*[c/255 for c in base_color])
        s *= mood_params['saturation']
        
        # Ensure contrast
        if avg_lum > 0.5:
            v = min(v, 0.6)  # Darker for light backgrounds
        else:
            v = max(v, 0.8)  # Brighter for dark backgrounds
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r*255), int(g*255), int(b*255))
    
    def _add_adaptive_gradient(self, image, genre, mood_params, layout_config):
        """Add mood and layout-aware gradient"""
        w, h = image.size
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        strength = mood_params['gradient_strength']
        title_y = layout_config['title_y']
        
        # Gradient direction based on layout
        if title_y < 0.3:  # Top
            gradient_range = int(h * 0.4)
            for i in range(gradient_range):
                alpha = int(200 * strength * (1 - i / gradient_range))
                draw.rectangle([(0, i), (w, i+1)], fill=(0, 0, 0, alpha))
        elif title_y > 0.7:  # Bottom
            gradient_range = int(h * 0.4)
            for i in range(gradient_range):
                alpha = int(200 * strength * (i / gradient_range))
                draw.rectangle([(0, h - gradient_range + i), (w, h - gradient_range + i + 1)], 
                             fill=(0, 0, 0, alpha))
        else:  # Middle
            gradient_range = int(h * 0.3)
            center_y = int(h * title_y)
            for i in range(gradient_range):
                alpha = int(150 * strength * (1 - abs(i - gradient_range/2) / (gradient_range/2)))
                draw.rectangle([(0, center_y - gradient_range//2 + i), 
                              (w, center_y - gradient_range//2 + i + 1)], 
                             fill=(0, 0, 0, alpha))
        
        return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    
    def _add_enhanced_title(self, image, title, genre, layout_config, title_variant, 
                           text_color, mood_params):
        """Add title with multi-layer effects"""
        w, h = image.size
        
        # Apply caps if needed
        if title_variant.get('caps', False):
            title = title.upper()
        
        # Load font
        try:
            font_size = int(h * 0.1)
            font = ImageFont.truetype(title_variant['title'], font_size)
        except:
            font = ImageFont.load_default()
        
        # Create text layer
        text_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Calculate position with margin
        margin = int(w * 0.05)
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Clamp text width
        if text_w > w - 2 * margin:
            text_w = w - 2 * margin
        
        align = layout_config['align']
        if align == 'center':
            x = (w - text_w) // 2
        elif align == 'left':
            x = margin
        else:  # right
            x = w - text_w - margin
        
        # Clamp x
        x = max(margin, min(x, w - text_w - margin))
        
        y = int(h * layout_config['title_y'])
        # Clamp y
        y = max(margin, min(y, h - text_h - margin))
        
        # Multi-layer shadows
        effect_config = self.effects.get(genre, self.effects['action'])
        for i in range(effect_config['shadow_layers']):
            offset = (i + 1) * 3
            alpha = 180 - i * 40
            draw.text((x + offset, y + offset), title, font=font, fill=(0, 0, 0, alpha))
        
        # Glow effect
        if effect_config['glow'] and mood_params['glow_intensity'] > 0:
            glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_color = (*text_color, int(100 * mood_params['glow_intensity']))
            for offset in range(1, 6):
                glow_draw.text((x + offset, y), title, font=font, fill=glow_color)
                glow_draw.text((x - offset, y), title, font=font, fill=glow_color)
                glow_draw.text((x, y + offset), title, font=font, fill=glow_color)
                glow_draw.text((x, y - offset), title, font=font, fill=glow_color)
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(3))
            text_layer = Image.alpha_composite(text_layer, glow_layer)
            draw = ImageDraw.Draw(text_layer)
        
        # Outline
        for ox, oy in [(-2,-2),(-2,2),(2,-2),(2,2),(-2,0),(2,0),(0,-2),(0,2)]:
            draw.text((x+ox, y+oy), title, font=font, fill=(0, 0, 0, 255))
        
        # Main text
        draw.text((x, y), title, font=font, fill=text_color)
        
        # Rotation if needed
        rotation = layout_config.get('rotation', 0)
        if rotation != 0:
            text_layer = text_layer.rotate(rotation, expand=False, center=(x + text_w//2, y))
        
        return Image.alpha_composite(image.convert('RGBA'), text_layer).convert('RGB')
    
    def _add_enhanced_tagline(self, image, tagline, genre, layout_config, typo, 
                             text_color, mood_params):
        """Add tagline with subtle effects"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.025)
            font = ImageFont.truetype(typo['tagline'], font_size)
        except:
            font = ImageFont.load_default()
        
        margin = int(w * 0.05)
        bbox = draw.textbbox((0, 0), tagline, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        align = layout_config['align']
        if align == 'center':
            x = (w - text_w) // 2
        elif align == 'left':
            x = margin
        else:
            x = w - text_w - margin
        
        # Clamp x and y
        x = max(margin, min(x, w - text_w - margin))
        y = int(h * layout_config['tagline_y'])
        y = max(margin, min(y, h - text_h - margin))
        
        # Shadow
        draw.text((x + 1, y + 1), tagline, font=font, fill=(0, 0, 0, 150))
        
        # Lighter version of text color
        light_color = tuple(min(255, int(c * 1.2)) for c in text_color[:3])
        draw.text((x, y), tagline, font=font, fill=light_color)
        
        return image
    
    def _add_credits(self, image, credits, typo, layout_config):
        """Add credits at bottom"""
        w, h = image.size
        draw = ImageDraw.Draw(image)
        
        try:
            font_size = int(h * 0.018)
            font = ImageFont.truetype(typo['credits'], font_size)
        except:
            font = ImageFont.load_default()
        
        margin = int(w * 0.05)
        bbox = draw.textbbox((0, 0), credits, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (w - text_w) // 2
        x = max(margin, min(x, w - text_w - margin))
        
        y = h - text_h - margin
        y = max(margin, y)
        
        draw.text((x, y), credits, font=font, fill=(180, 180, 180))
        return image
    
    def add_poster_text_variants(self, image, title, genre='action', tagline=None, 
                                credits=None, mood='epic', num_variants=3):
        """Generate multiple stylistic variants"""
        variants = []
        layouts = self.genre_layouts.get(genre, ['centered', 'hero', 'festival'])
        
        for i in range(num_variants):
            layout = layouts[i % len(layouts)]
            variant = self.add_poster_text(
                image.copy(), title, genre, tagline, credits,
                layout=layout, mood=mood, variant_seed=i
            )
            variants.append((variant, layout))
        
        return variants
