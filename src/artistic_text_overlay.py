"""Professional movie poster text with advanced typography and artistic effects"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random

class ArtisticTextOverlay:
    def __init__(self):
        # Genre-specific style configurations
        self.genre_styles = {
            'action': {
                'fonts': ['impact', 'arial_black'],
                'sizes': [0.16, 0.13],
                'colors': [(255, 40, 40), (255, 255, 255)],
                'angles': [-8, -5, -3],
                'outline': 10,
                'shadow': 22,
                'glow': None,
                'spacing': 1.2,
                'layout': 'stacked_angled'
            },
            'horror': {
                'fonts': ['impact'],
                'sizes': [0.18],
                'colors': [(120, 0, 0), (200, 50, 50)],
                'angles': [0],
                'outline': 12,
                'shadow': 30,
                'glow': None,
                'spacing': 1.0,
                'layout': 'centered_massive'
            },
            'thriller': {
                'fonts': ['impact'],
                'sizes': [0.18, 0.15, 0.13],
                'colors': [(255, 255, 255)],
                'angles': [-12, -10, -8],
                'outline': 8,
                'shadow': 18,
                'glow': None,
                'spacing': 1.1,
                'layout': 'full_angled'
            },
            'scifi': {
                'fonts': ['impact'],
                'sizes': [0.15],
                'colors': [(255, 255, 255), (200, 255, 255)],
                'angles': [0],
                'outline': 7,
                'shadow': 0,
                'glow': [(0, 150, 255), (0, 200, 255), (100, 220, 255)],
                'spacing': 1.5,
                'layout': 'tracked_glow'
            },
            'fantasy': {
                'fonts': ['times_bold'],
                'sizes': [0.16, 0.13],
                'colors': [(255, 220, 120), (255, 240, 180)],
                'angles': [0],
                'outline': 7,
                'shadow': 0,
                'glow': [(255, 200, 0), (255, 220, 100)],
                'spacing': 1.15,
                'layout': 'stacked_glow'
            },
            'romance': {
                'fonts': ['georgia'],
                'sizes': [0.13],
                'colors': [(255, 245, 230), (255, 255, 255)],
                'angles': [0],
                'outline': 5,
                'shadow': 14,
                'glow': None,
                'spacing': 1.0,
                'layout': 'elegant_centered'
            },
            'drama': {
                'fonts': ['impact', 'times_bold'],
                'sizes': [0.14, 0.12],
                'colors': [(255, 255, 255)],
                'angles': [0],
                'outline': 7,
                'shadow': 16,
                'glow': None,
                'spacing': 1.2,
                'layout': 'split_bar'
            }
        }
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        base = 'C:/Windows/Fonts/'
        return {
            'impact': base + 'impact.ttf',
            'arial_black': base + 'ariblk.ttf',
            'times_bold': base + 'timesbd.ttf',
            'georgia': base + 'georgia.ttf',
        }
    
    def add_title(self, image, title, genre=None, style="cinematic"):
        """Main entry point for adding text to poster"""
        img = image.copy().convert('RGBA')
        w, h = img.size
        
        # Get style config
        genre_style = self.genre_styles.get(genre, self.genre_styles['drama'])
        palette = self._extract_palette(img)
        
        # Route to layout based on genre
        layout = genre_style['layout']
        if layout == 'stacked_angled':
            return self._stacked_angled_layout(img, title, genre_style, palette)
        elif layout == 'centered_massive':
            return self._centered_massive_layout(img, title, genre_style, palette)
        elif layout == 'full_angled':
            return self._full_angled_layout(img, title, genre_style, palette)
        elif layout == 'tracked_glow':
            return self._tracked_glow_layout(img, title, genre_style, palette)
        elif layout == 'stacked_glow':
            return self._stacked_glow_layout(img, title, genre_style, palette)
        elif layout == 'elegant_centered':
            return self._elegant_centered_layout(img, title, genre_style, palette)
        else:
            return self._split_bar_layout(img, title, genre_style, palette)
    
    def _extract_palette(self, img):
        """Extract color palette from image"""
        arr = np.array(img.convert('RGB').resize((100, 100)))
        pixels = arr.reshape(-1, 3)
        bright = pixels[pixels.mean(axis=1) > 150]
        dark = pixels[pixels.mean(axis=1) <= 80]
        return {
            'bright': tuple(bright.mean(axis=0).astype(int)) if len(bright) > 0 else (255, 200, 50),
            'dark': tuple(dark.mean(axis=0).astype(int)) if len(dark) > 0 else (0, 0, 0),
        }
    
    def _sample_background_region(self, img, y_start, y_end):
        """Sample background colors in text region"""
        w, h = img.size
        region = img.crop((0, max(0, y_start - 50), w, min(h, y_end + 50)))
        arr = np.array(region.convert('RGB'))
        pixels = arr.reshape(-1, 3)
        
        # Get dominant color via median
        dominant = np.median(pixels, axis=0).astype(int)
        avg_brightness = np.mean(pixels)
        
        return {
            'dominant': tuple(dominant),
            'brightness': avg_brightness,
            'is_dark': avg_brightness < 100,
            'is_bright': avg_brightness > 150
        }
    
    def _calculate_contrast(self, color1, color2):
        """Calculate contrast ratio between two colors"""
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb[:3]]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = luminance(color1)
        l2 = luminance(color2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    
    def _get_complementary_color(self, rgb):
        """Get complementary color"""
        r, g, b = rgb[:3]
        return (255 - r, 255 - g, 255 - b)
    
    def _adjust_for_contrast(self, color, background, min_contrast=4.5):
        """Adjust color to meet minimum contrast ratio"""
        contrast = self._calculate_contrast(color, background)
        
        if contrast >= min_contrast:
            return color
        
        # If contrast too low, use high-contrast fallback
        bg_brightness = sum(background[:3]) / 3
        if bg_brightness < 128:
            # Dark background -> bright text
            return (255, 255, 255)
        else:
            # Bright background -> dark text
            return (0, 0, 0)
    
    def _get_adaptive_colors(self, img, y_start, y_end, genre_style):
        """Get adaptive colors based on background"""
        # Sample background
        bg_info = self._sample_background_region(img, y_start, y_end)
        
        # Get base colors from genre style
        base_colors = genre_style['colors']
        
        # Adjust primary color for contrast
        primary = base_colors[0]
        primary_adjusted = self._adjust_for_contrast(primary, bg_info['dominant'])
        
        # Check if adjustment was needed
        if primary_adjusted != primary:
            # Use high-contrast fallback
            if bg_info['is_dark']:
                primary_color = (255, 255, 255)
                accent_color = (200, 200, 200)
            else:
                primary_color = (0, 0, 0)
                accent_color = (50, 50, 50)
        else:
            # Use genre colors with slight adjustment
            primary_color = primary
            if len(base_colors) > 1:
                accent_color = base_colors[1]
            else:
                # Create accent by adjusting brightness
                if bg_info['is_dark']:
                    accent_color = tuple(min(255, c + 50) for c in primary[:3])
                else:
                    accent_color = tuple(max(0, c - 50) for c in primary[:3])
        
        # Outline color (always high contrast with background)
        if bg_info['is_dark']:
            outline_color = (0, 0, 0)
        else:
            outline_color = (0, 0, 0)
        
        # Shadow color (darker version of background dominant)
        shadow_color = tuple(max(0, int(c * 0.3)) for c in bg_info['dominant'][:3])
        
        return {
            'primary': primary_color,
            'accent': accent_color,
            'outline': outline_color,
            'shadow': shadow_color,
            'contrast_ratio': self._calculate_contrast(primary_color, bg_info['dominant'])
        }
    
    def _stacked_angled_layout(self, img, title, style, palette):
        """Stacked words with varied angles"""
        w, h = img.size
        words = title.upper().split()
        base = img.copy()
        
        # Add vignette once
        base = self._add_vignette(base, h - 280, 280, 210)
        
        # Calculate safe layout
        margin = 40
        line_height = min(110, (h - margin * 2) // max(len(words), 1))
        
        # Render each word once
        for idx, word in enumerate(words):
            # Calculate position first for color sampling
            y_pos = h - (len(words) - idx) * line_height - margin
            
            # Get adaptive colors based on background
            adaptive_colors = self._get_adaptive_colors(img, y_pos, y_pos + line_height, style)
            
            # Get style for this word
            font_size = int(h * style['sizes'][min(idx, len(style['sizes'])-1)])
            font_name = style['fonts'][min(idx, len(style['fonts'])-1)]
            color = adaptive_colors['primary'] if idx == 0 else adaptive_colors['accent']
            angle = style['angles'][min(idx, len(style['angles'])-1)]
            
            # Add randomness within style
            angle += random.randint(-2, 2)
            
            # Create modified style with adaptive colors
            adaptive_style = style.copy()
            adaptive_style['colors'] = [adaptive_colors['primary'], adaptive_colors['accent']]
            
            # Create text layer with all effects
            text_layer = self._render_text_with_effects(
                word, font_name, font_size, color, adaptive_style, w, h
            )
            
            # Rotate if needed
            if angle != 0:
                text_layer = self._safe_rotate(text_layer, angle)
            
            # Position with bounds check
            x_offset = idx * 25
            text_layer = self._position_text(text_layer, w, h, x_offset, y_pos)
            
            # Composite once
            base = Image.alpha_composite(base, text_layer)
        
        return base.convert('RGB')
    
    def _centered_massive_layout(self, img, title, style, palette):
        """Large centered text"""
        w, h = img.size
        base = img.copy()
        title = title.upper()
        
        # Vignette
        base = self._add_vignette(base, h//2 - 125, 250, 200)
        
        # Calculate size with bounds check
        margin = 40
        font_size = int(h * style['sizes'][0])
        font_name = style['fonts'][0]
        y_pos = int(h * 0.60)
        
        # Get adaptive colors
        adaptive_colors = self._get_adaptive_colors(img, y_pos - 50, y_pos + 100, style)
        
        # Check if fits
        font = self._get_font(font_name, font_size)
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = temp_draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width > w - margin * 2:
            font_size = int(font_size * (w - margin * 2) / text_width)
        
        # Create modified style with adaptive colors
        adaptive_style = style.copy()
        adaptive_style['colors'] = [adaptive_colors['primary'], adaptive_colors['accent']]
        
        # Render once
        text_layer = self._render_text_with_effects(
            title, font_name, font_size, adaptive_colors['primary'], adaptive_style, w, h
        )
        text_layer = self._position_text(text_layer, w, h, 0, y_pos)
        
        base = Image.alpha_composite(base, text_layer)
        return base.convert('RGB')
    
    def _full_angled_layout(self, img, title, style, palette):
        """Full composition rotated"""
        w, h = img.size
        base = img.copy()
        words = title.upper().split()
        
        # Create composition
        margin = 40
        line_height = min(90, (h - margin * 2) // max(len(words), 1))
        comp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        
        # Render each word once
        for idx, word in enumerate(words):
            font_size = int(h * style['sizes'][min(idx, len(style['sizes'])-1)])
            font_name = style['fonts'][0]
            
            text_layer = self._render_text_with_effects(
                word, font_name, font_size, style['colors'][0], style, w, h
            )
            
            y_pos = margin + idx * line_height
            x_offset = (idx % 2) * 40 - 20
            text_layer = self._position_text(text_layer, w, h, x_offset, y_pos)
            
            comp = Image.alpha_composite(comp, text_layer)
        
        # Rotate entire composition once
        angle = style['angles'][0] + random.randint(-2, 2)
        comp = self._safe_rotate(comp, angle)
        base = Image.alpha_composite(base, comp)
        
        return base.convert('RGB')
    
    def _tracked_glow_layout(self, img, title, style, palette):
        """Wide letter spacing with glow"""
        w, h = img.size
        base = img.copy()
        title = title.upper()
        
        # Background
        base = self._add_vignette(base, h//2 - 140, 280, 210)
        
        # Calculate spacing
        margin = 40
        font_size = int(h * style['sizes'][0])
        font = self._get_font(style['fonts'][0], font_size)
        spacing = int(font_size * (style['spacing'] - 1.0))
        
        # Measure
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        char_widths = [temp_draw.textbbox((0, 0), c, font=font)[2] for c in title]
        total_width = sum(char_widths) + spacing * (len(title) - 1)
        
        # Scale if needed
        if total_width > w - margin * 2:
            scale = (w - margin * 2) / total_width
            font_size = int(font_size * scale)
            font = self._get_font(style['fonts'][0], font_size)
            spacing = int(font_size * (style['spacing'] - 1.0))
            char_widths = [temp_draw.textbbox((0, 0), c, font=font)[2] for c in title]
            total_width = sum(char_widths) + spacing * (len(title) - 1)
        
        y = int(h * 0.45)
        
        # Glow pass (separate)
        if style['glow']:
            for glow_color in style['glow']:
                for radius in [35, 25, 15]:
                    glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                    gd = ImageDraw.Draw(glow_layer)
                    x_pos = (w - total_width) // 2
                    for char in title:
                        gd.text((x_pos, y), char, font=font, fill=(*glow_color, int(140 * radius/35)))
                        x_pos += temp_draw.textbbox((0, 0), char, font=font)[2] + spacing
                    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius))
                    base = Image.alpha_composite(base, glow_layer)
        
        # Text pass (separate)
        text_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        td = ImageDraw.Draw(text_layer)
        x_pos = (w - total_width) // 2
        
        for char in title:
            # Outline
            for t in [style['outline'], max(3, style['outline']-2)]:
                for dx in range(-t, t+1):
                    for dy in range(-t, t+1):
                        if dx*dx + dy*dy <= t*t:
                            td.text((x_pos + dx, y + dy), char, font=font, fill=(0, 0, 0, 230))
            
            # Main text
            td.text((x_pos, y), char, font=font, fill=(*style['colors'][0], 255))
            
            # Highlight
            if len(style['colors']) > 1:
                td.text((x_pos-1, y-1), char, font=font, fill=(*style['colors'][1], 100))
            
            x_pos += temp_draw.textbbox((0, 0), char, font=font)[2] + spacing
        
        base = Image.alpha_composite(base, text_layer)
        return base.convert('RGB')
    
    def _stacked_glow_layout(self, img, title, style, palette):
        """Stacked with glow"""
        w, h = img.size
        base = img.copy()
        words = title.upper().split()
        
        # Vignette
        base = self._add_vignette(base, h - 220, 220, 190)
        
        # Layout
        margin = 40
        line_height = min(95, (h - margin * 2) // max(len(words), 1))
        
        # Render each word once
        for idx, word in enumerate(words):
            font_size = int(h * style['sizes'][min(idx, len(style['sizes'])-1)])
            font_name = style['fonts'][0]
            font = self._get_font(font_name, font_size)
            
            # Check width
            temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            bbox = temp_draw.textbbox((0, 0), word, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > w - margin * 2:
                font_size = int(font_size * (w - margin * 2) / text_width)
                font = self._get_font(font_name, font_size)
            
            y_pos = h - (len(words) - idx) * line_height - margin
            
            # Glow pass
            if style['glow']:
                for glow_color in style['glow']:
                    for radius in [25, 15]:
                        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                        gd = ImageDraw.Draw(glow)
                        bbox = gd.textbbox((0, 0), word, font=font)
                        x = (w - (bbox[2] - bbox[0])) // 2
                        gd.text((x, y_pos), word, font=font, fill=(*glow_color, int(120 * radius/25)))
                        glow = glow.filter(ImageFilter.GaussianBlur(radius))
                        base = Image.alpha_composite(base, glow)
            
            # Text pass
            text_layer = self._render_text_with_effects(
                word, font_name, font_size, style['colors'][0], style, w, h
            )
            text_layer = self._position_text(text_layer, w, h, 0, y_pos)
            base = Image.alpha_composite(base, text_layer)
        
        return base.convert('RGB')
    
    def _elegant_centered_layout(self, img, title, style, palette):
        """Elegant centered"""
        w, h = img.size
        base = img.copy()
        title = title.upper()
        
        # Vignette
        base = self._add_vignette(base, h - 200, 200, 150)
        
        # Size check
        margin = 40
        font_size = int(h * style['sizes'][0])
        font_name = style['fonts'][0]
        font = self._get_font(font_name, font_size)
        y_pos = h - 90
        
        # Get adaptive colors
        adaptive_colors = self._get_adaptive_colors(img, y_pos - 50, y_pos + 50, style)
        
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = temp_draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width > w - margin * 2:
            font_size = int(font_size * (w - margin * 2) / text_width)
        
        # Shadow pass with adaptive shadow color
        if style['shadow'] > 0:
            shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            font = self._get_font(font_name, font_size)
            bbox = sd.textbbox((0, 0), title, font=font)
            x = (w - (bbox[2] - bbox[0])) // 2
            y = h - (bbox[3] - bbox[1]) - 90
            shadow_color = adaptive_colors['shadow']
            for i in range(style['shadow'], 0, -1):
                sd.text((x + i*0.7, y + i*0.7), title, font=font, fill=(*shadow_color, int(140 * i/style['shadow'])))
            shadow = shadow.filter(ImageFilter.GaussianBlur(8))
            base = Image.alpha_composite(base, shadow)
        
        # Create modified style with adaptive colors
        adaptive_style = style.copy()
        adaptive_style['colors'] = [adaptive_colors['primary'], adaptive_colors['accent']]
        
        # Text pass
        text_layer = self._render_text_with_effects(
            title, font_name, font_size, adaptive_colors['primary'], adaptive_style, w, h
        )
        text_layer = self._position_text(text_layer, w, h, 0, y_pos)
        base = Image.alpha_composite(base, text_layer)
        
        return base.convert('RGB')
    
    def _split_bar_layout(self, img, title, style, palette):
        """Two-line split with bar"""
        w, h = img.size
        base = img.copy()
        words = title.upper().split()
        
        # Split lines
        if len(words) >= 2:
            mid = len(words) // 2
            lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
        else:
            lines = [title.upper()]
        
        # Bar
        bar_h = 230
        bar_y = h - bar_h - 20
        bar = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bar)
        for i in range(bar_h):
            alpha = int(230 * (i / bar_h) ** 1.15)
            bd.rectangle([(0, bar_y + i), (w, bar_y + i + 1)], fill=(0, 0, 0, alpha))
        bd.rectangle([(0, bar_y), (w, bar_y + 5)], fill=(*palette['bright'], 240))
        base = Image.alpha_composite(base, bar)
        
        # Render lines
        margin = 40
        line_spacing = 100
        
        for idx, line in enumerate(lines):
            if not line:
                continue
            
            font_name = style['fonts'][min(idx, len(style['fonts'])-1)]
            font_size = int(h * style['sizes'][min(idx, len(style['sizes'])-1)])
            font = self._get_font(font_name, font_size)
            
            # Check width
            temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > w - margin * 2:
                font_size = int(font_size * (w - margin * 2) / text_width)
            
            y_pos = bar_y + 40 + idx * line_spacing
            
            # Shadow pass
            if style['shadow'] > 0:
                shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                sd = ImageDraw.Draw(shadow)
                font = self._get_font(font_name, font_size)
                bbox = sd.textbbox((0, 0), line, font=font)
                x = (w - (bbox[2] - bbox[0])) // 2
                for i in range(style['shadow'], 0, -1):
                    sd.text((x + i*0.8, y_pos + i*0.8), line, font=font, fill=(0, 0, 0, int(180 * i/style['shadow'])))
                shadow = shadow.filter(ImageFilter.GaussianBlur(5))
                base = Image.alpha_composite(base, shadow)
            
            # Text pass
            text_layer = self._render_text_with_effects(
                line, font_name, font_size, style['colors'][0], style, w, h
            )
            text_layer = self._position_text(text_layer, w, h, 0, y_pos)
            base = Image.alpha_composite(base, text_layer)
        
        return base.convert('RGB')
    
    def _render_text_with_effects(self, text, font_name, font_size, color, style, w, h):
        """Render text with outline and highlight - single pass per effect"""
        font = self._get_font(font_name, font_size)
        
        # Measure
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (w - text_w) // 2
        y = (h - text_h) // 2
        
        # Create layers
        outline_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        text_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        highlight_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        
        od = ImageDraw.Draw(outline_layer)
        td = ImageDraw.Draw(text_layer)
        hd = ImageDraw.Draw(highlight_layer)
        
        # Outline (drawn once)
        for t in [style['outline'], max(3, style['outline']-3)]:
            for dx in range(-t, t+1):
                for dy in range(-t, t+1):
                    if dx*dx + dy*dy <= t*t:
                        od.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
        
        # Main text (drawn once)
        td.text((x, y), text, font=font, fill=(*color, 255))
        
        # Highlight (drawn once if applicable)
        if len(style['colors']) > 1:
            hd.text((x-2, y-2), text, font=font, fill=(*style['colors'][1], 90))
        
        # Composite
        result = outline_layer
        result = Image.alpha_composite(result, text_layer)
        result = Image.alpha_composite(result, highlight_layer)
        
        return result
    
    def _add_vignette(self, img, start_y, height, max_alpha):
        """Add gradient vignette"""
        vignette = Image.new('RGBA', img.size, (0, 0, 0, 0))
        vd = ImageDraw.Draw(vignette)
        for i in range(height):
            alpha = int(max_alpha * (i / height) ** 1.1)
            vd.rectangle([(0, start_y + i), (img.size[0], start_y + i + 1)], fill=(0, 0, 0, alpha))
        return Image.alpha_composite(img, vignette)
    
    def _safe_rotate(self, img, angle):
        """Rotate with oversized canvas"""
        if angle == 0:
            return img
        w, h = img.size
        canvas_size = max(w, h) * 3
        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
        canvas.paste(img, ((canvas_size - w) // 2, (canvas_size - h) // 2))
        canvas = canvas.rotate(angle, expand=False, resample=Image.BICUBIC)
        crop_x = (canvas_size - w) // 2
        crop_y = (canvas_size - h) // 2
        return canvas.crop((crop_x, crop_y, crop_x + w, crop_y + h))
    
    def _position_text(self, layer, target_w, target_h, x_offset, y_offset):
        """Position text layer with bounds check"""
        result = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        bbox = layer.getbbox()
        if bbox:
            text_img = layer.crop(bbox)
            tw, th = text_img.size
            x = (target_w - tw) // 2 + x_offset
            y = y_offset
            x = max(0, min(x, target_w - tw))
            y = max(0, min(y, target_h - th))
            result.paste(text_img, (x, y), text_img)
        return result
    
    def _get_font(self, name, size):
        """Load font with fallback"""
        try:
            return ImageFont.truetype(self.fonts.get(name, self.fonts['impact']), size)
        except:
            return ImageFont.load_default()
