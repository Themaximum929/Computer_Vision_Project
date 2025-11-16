from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
import numpy as np
from pathlib import Path
import colorsys
import random

class CinematicTextOverlay:
    FONT_CATEGORIES = {
        "serif": ["times", "georgia", "garamond", "baskerville", "palatino"],
        "sans_serif": ["arial", "helvetica", "futura", "roboto", "montserrat"],
        "display": ["impact", "bebas", "oswald", "anton", "bangers"],
        "decorative": ["comic", "papyrus", "brush", "script", "gothic"]
    }
    
    GENRE_FONT_RULES = {
        "action": {"category": "display", "fallback": "sans_serif", "bold": True, "layout": "stacked_angled"},
        "horror": {"category": "decorative", "fallback": "display", "bold": True, "layout": "centered_massive"},
        "scifi": {"category": "sans_serif", "fallback": "sans_serif", "bold": False, "layout": "tracked_wide"},
        "drama": {"category": "serif", "fallback": "serif", "bold": False, "layout": "elegant_bottom"},
        "comedy": {"category": "decorative", "fallback": "sans_serif", "bold": False, "layout": "stacked_angled"},
        "thriller": {"category": "sans_serif", "fallback": "serif", "bold": True, "layout": "full_angled"},
        "fantasy": {"category": "decorative", "fallback": "serif", "bold": False, "layout": "stacked_centered"},
        "romance": {"category": "serif", "fallback": "sans_serif", "bold": False, "layout": "elegant_bottom"},
        "epic": {"category": "serif", "fallback": "serif", "bold": True, "layout": "stacked_angled"},
        "historical": {"category": "serif", "fallback": "serif", "bold": False, "layout": "elegant_bottom"},
        "modern": {"category": "sans_serif", "fallback": "sans_serif", "bold": False, "layout": "tracked_wide"},
        "minimalist": {"category": "sans_serif", "fallback": "sans_serif", "bold": False, "layout": "elegant_bottom"},
        "cinematic": {"category": "sans_serif", "fallback": "serif", "bold": True, "layout": "stacked_angled"}
    }
    
    def __init__(self, fonts_dir="fonts/cinematic"):
        self.fonts_dir = Path(fonts_dir)
        self.available_fonts = self._scan_fonts()
        self.categorized_fonts = self._categorize_fonts()
        
    def _scan_fonts(self):
        """Scan fonts directory for .ttf and .otf files"""
        if not self.fonts_dir.exists():
            self.fonts_dir.mkdir(parents=True, exist_ok=True)
        fonts = list(self.fonts_dir.glob("*.ttf")) + list(self.fonts_dir.glob("*.otf"))
        if not fonts:
            fonts = self._get_system_fonts()
        return {f.stem.lower(): str(f) for f in fonts}
    
    def _categorize_fonts(self):
        """Categorize available fonts by type"""
        categorized = {cat: [] for cat in self.FONT_CATEGORIES}
        for font_name in self.available_fonts:
            for category, keywords in self.FONT_CATEGORIES.items():
                if any(kw in font_name.lower() for kw in keywords):
                    categorized[category].append(font_name)
                    break
            else:
                categorized["sans_serif"].append(font_name)
        return categorized
    
    def _get_system_fonts(self):
        """Fallback to system fonts"""
        system_fonts = ["arial.ttf", "impact.ttf", "times.ttf", "comic.ttf"]
        return [Path(f) for f in system_fonts if Path(f).exists()]
    
    def analyze_background(self, image, region="bottom"):
        """Analyze background color in specified region"""
        w, h = image.size
        if region == "bottom":
            crop = image.crop((0, int(h*0.7), w, h))
        elif region == "top":
            crop = image.crop((0, 0, w, int(h*0.3)))
        else:
            crop = image.crop((0, int(h*0.4), w, int(h*0.6)))
        
        arr = np.array(crop)
        avg_color = arr.mean(axis=(0, 1))
        brightness = np.mean(avg_color)
        
        return {
            "avg_color": tuple(avg_color.astype(int)),
            "brightness": brightness,
            "is_dark": brightness < 128
        }
    
    def get_adaptive_color(self, bg_analysis, genre=None):
        """Pick high contrast text color based on background brightness"""
        brightness = bg_analysis["brightness"]
        
        if brightness < 128:
            return (255, 255, 255)
        else:
            return (0, 0, 0)
    
    def auto_select_font(self, genre=None):
        """Select font based on genre using category rules"""
        if not genre or genre not in self.GENRE_FONT_RULES:
            genre = "cinematic"
        
        rules = self.GENRE_FONT_RULES[genre]
        primary_cat = rules["category"]
        fallback_cat = rules["fallback"]
        
        print(f"    Font selection for genre '{genre}':")
        print(f"      Primary category: {primary_cat}")
        print(f"      Available fonts in {primary_cat}: {self.categorized_fonts[primary_cat]}")
        
        if self.categorized_fonts[primary_cat]:
            font_name = self.categorized_fonts[primary_cat][0]
            font_path = self.available_fonts[font_name]
            print(f"      ✓ Selected: {font_name} ({font_path})")
            return font_path
        
        print(f"      Fallback category: {fallback_cat}")
        if self.categorized_fonts[fallback_cat]:
            font_name = self.categorized_fonts[fallback_cat][0]
            font_path = self.available_fonts[font_name]
            print(f"      ✓ Selected: {font_name} ({font_path})")
            return font_path
        
        if self.available_fonts:
            font_path = list(self.available_fonts.values())[0]
            print(f"      ✓ Using first available: {font_path}")
            return font_path
        
        print(f"      ⚠ No custom fonts found, using system default")
        return "arial.ttf"
    
    def calculate_safe_bounds(self, image, text, font, position):
        """Calculate text position ensuring it stays within bounds"""
        draw = ImageDraw.Draw(image)
        w, h = image.size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        h_margin = int(w * 0.08)
        v_margin = int(h * 0.08)
        
        max_text_w = w - (2 * h_margin)
        if text_w > max_text_w:
            text_w = max_text_w
        
        x = (w - text_w) // 2
        x = max(h_margin, min(x, w - text_w - h_margin))
        
        if position == "top":
            y = v_margin
        elif position == "center":
            y = max(v_margin, (h - text_h) // 2)
        else:
            y = h - text_h - v_margin
        
        y = max(v_margin, min(y, h - text_h - v_margin))
        
        return x, y
    
    def get_readability_effects(self, genre, bg_analysis):
        """Get optimal effects for readability based on genre and background"""
        rules = self.GENRE_FONT_RULES.get(genre, self.GENRE_FONT_RULES["cinematic"])
        
        if bg_analysis["is_dark"]:
            stroke = 2 if rules["bold"] else 1
            shadow = 4 if rules["bold"] else 3
        else:
            stroke = 3 if rules["bold"] else 2
            shadow = 6 if rules["bold"] else 4
        
        return {"stroke_width": stroke, "shadow_offset": shadow}
    
    def _layout_stacked_angled(self, img, text, genre, auto_adapt):
        """Action/Epic: Stacked words with varied angles"""
        print(f"    Using STACKED_ANGLED layout for genre: {genre}")
        w, h = img.size
        words = text.upper().split()
        base = img.copy()
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        v_margin = int(h * 0.10)
        angles = [-8, -5, -3, 0]
        
        max_width = w - 2 * margin
        font_size = int(h * 0.30)
        
        for word in words:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            bbox = draw.textbbox((0, 0), word, font=font)
            if bbox[2] - bbox[0] > max_width:
                font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
        
        line_height = int(font_size * 1.15)
        total_height = len(words) * line_height
        y_start = max(v_margin, h - total_height - v_margin)
        
        for idx, word in enumerate(words):
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            y = y_start + idx * line_height
            if y + line_height > h - v_margin:
                break
            bg_analysis = self.analyze_background(base, "bottom")
            color = self.get_adaptive_color(bg_analysis, genre)
            
            word_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(word_layer)
            
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2 + idx * 15
            x = max(margin, min(x, w - text_w - margin))
            
            for i in range(5, 0, -1):
                draw.text((x + i, y + i), word, font=font, fill=(0, 0, 0, 140))
            
            draw.text((x, y), word, font=font, fill=(0, 0, 0), 
                     stroke_width=5, stroke_fill=(0, 0, 0))
            draw.text((x, y), word, font=font, fill=color)
            
            angle = angles[min(idx, len(angles)-1)] + random.randint(-2, 2)
            if angle != 0:
                word_layer = word_layer.rotate(angle, expand=False, resample=Image.BICUBIC)
            
            base = Image.alpha_composite(base, word_layer)
        
        return base.convert('RGB')
    
    def _layout_centered_massive(self, img, text, genre, auto_adapt):
        """Horror: Large centered text"""
        print(f"    Using CENTERED_MASSIVE layout for genre: {genre}")
        w, h = img.size
        base = img.copy()
        title = text.upper()
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        max_width = w - 2 * margin
        font_size = int(h * 0.35)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        bbox = draw.textbbox((0, 0), title, font=font)
        
        if bbox[2] - bbox[0] > max_width:
            font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
        
        y = int(h * 0.40)
        bg_analysis = self.analyze_background(base, "center")
        color = self.get_adaptive_color(bg_analysis, genre)
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        
        for i in range(15, 0, -2):
            draw.text((x + i*0.4, y + i*0.4), title, font=font, fill=(0, 0, 0, 110))
        
        draw.text((x, y), title, font=font, fill=(0, 0, 0), 
                 stroke_width=8, stroke_fill=(0, 0, 0))
        draw.text((x, y), title, font=font, fill=color)
        
        base = Image.alpha_composite(base, overlay)
        return base.convert('RGB')
    
    def _layout_tracked_wide(self, img, text, genre, auto_adapt):
        """Sci-Fi: Wide letter spacing with multi-line support"""
        print(f"    Using TRACKED_WIDE layout for genre: {genre}")
        w, h = img.size
        base = img.copy()
        words = text.upper().split()
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        v_margin = int(h * 0.10)
        
        bg_analysis = self.analyze_background(base, "bottom")
        color = self.get_adaptive_color(bg_analysis, genre)
        
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        max_width = w - 2 * margin
        font_size = int(h * 0.25)
        
        for word in words:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), word, font=font)
            if bbox[2] - bbox[0] > max_width:
                font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        line_height = int(font_size * 1.2)
        total_height = len(words) * line_height
        y_start = max(v_margin, h - total_height - v_margin)
        
        for idx, word in enumerate(words):
            y = y_start + idx * line_height
            if y + line_height > h - v_margin:
                break
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2
            
            draw.text((x, y), word, font=font, fill=(0, 0, 0), 
                     stroke_width=3, stroke_fill=(0, 0, 0))
            draw.text((x, y), word, font=font, fill=color)
        
        base = Image.alpha_composite(base, overlay)
        return base.convert('RGB')
    
    def _layout_elegant_bottom(self, img, text, genre, auto_adapt):
        """Drama/Romance: Elegant bottom placement with multi-line support"""
        print(f"    Using ELEGANT_BOTTOM layout for genre: {genre}")
        w, h = img.size
        base = img.copy()
        words = text.upper().split()
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        v_margin = int(h * 0.10)
        
        bg_analysis = self.analyze_background(base, "bottom")
        color = self.get_adaptive_color(bg_analysis, genre)
        
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        max_width = w - 2 * margin
        font_size = int(h * 0.24)
        
        for word in words:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), word, font=font)
            if bbox[2] - bbox[0] > max_width:
                font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        line_height = int(font_size * 1.15)
        total_height = len(words) * line_height
        y_start = max(v_margin, h - total_height - v_margin)
        
        for idx, word in enumerate(words):
            y = y_start + idx * line_height
            if y + line_height > h - v_margin:
                break
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2
            
            for i in range(8, 0, -1):
                draw.text((x + i*0.4, y + i*0.4), word, font=font, fill=(0, 0, 0, 100))
            
            draw.text((x, y), word, font=font, fill=(0, 0, 0), 
                     stroke_width=3, stroke_fill=(0, 0, 0))
            draw.text((x, y), word, font=font, fill=color)
        
        base = Image.alpha_composite(base, overlay)
        return base.convert('RGB')
    
    def _layout_full_angled(self, img, text, genre, auto_adapt):
        """Thriller: Full composition angled"""
        print(f"    Using FULL_ANGLED layout for genre: {genre}")
        w, h = img.size
        words = text.upper().split()
        comp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        v_margin = int(h * 0.10)
        
        max_width = w - 2 * margin
        font_size = int(h * 0.28)
        
        for word in words:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            bbox = draw.textbbox((0, 0), word, font=font)
            if bbox[2] - bbox[0] > max_width:
                font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
        
        line_height = int(font_size * 1.15)
        
        for idx, word in enumerate(words):
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            y = v_margin + idx * line_height
            if y + line_height > h - v_margin:
                break
            
            word_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(word_layer)
            
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2 + (idx % 2) * 25 - 12
            x = max(margin, min(x, w - text_w - margin))
            
            draw.text((x, y), word, font=font, fill=(0, 0, 0), 
                     stroke_width=5, stroke_fill=(0, 0, 0))
            draw.text((x, y), word, font=font, fill=(255, 255, 255))
            
            comp = Image.alpha_composite(comp, word_layer)
        
        angle = -10 + random.randint(-2, 2)
        comp = comp.rotate(angle, expand=False, resample=Image.BICUBIC)
        
        base = img.copy()
        base = Image.alpha_composite(base, comp)
        return base.convert('RGB')
    
    def _layout_stacked_centered(self, img, text, genre, auto_adapt):
        """Fantasy: Stacked centered"""
        print(f"    Using STACKED_CENTERED layout for genre: {genre}")
        w, h = img.size
        words = text.upper().split()
        base = img.copy()
        
        font_path = self.auto_select_font(genre)
        margin = int(w * 0.10)
        v_margin = int(h * 0.10)
        
        max_width = w - 2 * margin
        font_size = int(h * 0.28)
        
        for word in words:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            bbox = draw.textbbox((0, 0), word, font=font)
            if bbox[2] - bbox[0] > max_width:
                font_size = int(font_size * max_width / (bbox[2] - bbox[0]) * 0.95)
        
        line_height = int(font_size * 1.15)
        total_height = len(words) * line_height
        y_start = max(v_margin, h - total_height - v_margin)
        
        for idx, word in enumerate(words):
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            y = y_start + idx * line_height
            if y + line_height > h - v_margin:
                break
            bg_analysis = self.analyze_background(base, "bottom")
            color = self.get_adaptive_color(bg_analysis, genre)
            
            overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2
            
            draw.text((x, y), word, font=font, fill=(0, 0, 0), 
                     stroke_width=5, stroke_fill=(0, 0, 0))
            draw.text((x, y), word, font=font, fill=color)
            
            base = Image.alpha_composite(base, overlay)
        
        return base.convert('RGB')
    
    def _render_multi_line(self, img, words, font, font_size, color, position, 
                           stroke_width, shadow_offset, angle, genre):
        """Render text with each word on separate line with optional angles"""
        w, h = img.size
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        
        margin = int(h * 0.08)
        line_height = int(h * 0.12)
        
        angles = [-8, -5, -3, 0] if angle != 0 else [0] * len(words)
        
        for idx, word in enumerate(words):
            word_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(word_overlay)
            
            word_angle = angles[min(idx, len(angles)-1)]
            
            if position == "bottom":
                y = h - (len(words) - idx) * line_height - margin
            elif position == "top":
                y = margin + idx * line_height
            else:
                y = (h - len(words) * line_height) // 2 + idx * line_height
            
            bbox = draw.textbbox((0, 0), word, font=font)
            text_w = bbox[2] - bbox[0]
            x = (w - text_w) // 2 + idx * 20
            
            draw.text((x + shadow_offset, y + shadow_offset), word, 
                     font=font, fill=(0, 0, 0, 180))
            
            if stroke_width > 0:
                draw.text((x, y), word, font=font, fill=(0, 0, 0),
                         stroke_width=stroke_width, stroke_fill=(0, 0, 0))
            
            draw.text((x, y), word, font=font, fill=color)
            
            if word_angle != 0:
                word_overlay = word_overlay.rotate(word_angle, expand=False, resample=Image.BICUBIC)
            
            overlay = Image.alpha_composite(overlay, word_overlay)
        
        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
    
    def fit_text_to_width(self, text, font, max_width, draw):
        """Reduce font size to fit text within max width"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        
        if text_w <= max_width:
            return text, font
        
        font_path = font.path if hasattr(font, 'path') else None
        if not font_path:
            return text, font
        
        current_size = font.size
        scale = max_width / text_w
        new_size = int(current_size * scale * 0.95)
        
        try:
            new_font = ImageFont.truetype(font_path, new_size)
            return text, new_font
        except:
            return text, font
    
    def add_text(self, image, text, font_path=None, font_size=None, color=None, 
                 position="bottom", stroke_width=None, shadow_offset=None, letter_spacing=5,
                 genre=None, auto_adapt=True, angle=0, multi_line=True):
        """Add text overlay with genre-specific professional layouts"""
        img = image.copy().convert('RGBA')
        genre = genre or "cinematic"
        
        rules = self.GENRE_FONT_RULES.get(genre, self.GENRE_FONT_RULES["cinematic"])
        layout = rules.get("layout", "stacked_angled")
        
        if layout == "stacked_angled":
            return self._layout_stacked_angled(img, text, genre, auto_adapt)
        elif layout == "centered_massive":
            return self._layout_centered_massive(img, text, genre, auto_adapt)
        elif layout == "tracked_wide":
            return self._layout_tracked_wide(img, text, genre, auto_adapt)
        elif layout == "elegant_bottom":
            return self._layout_elegant_bottom(img, text, genre, auto_adapt)
        elif layout == "full_angled":
            return self._layout_full_angled(img, text, genre, auto_adapt)
        else:
            return self._layout_stacked_centered(img, text, genre, auto_adapt)
