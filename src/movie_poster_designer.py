from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime, timedelta
from pathlib import Path

class MoviePosterDesigner:
    """Complete movie poster design with title, tagline, credits, date, rating"""
    
    GENRE_TAGLINES = {
        "action": ["The fight begins", "No mercy", "One last mission", "Justice will be served"],
        "horror": ["Fear has a new face", "Don't look back", "Evil awakens", "Nowhere to hide"],
        "scifi": ["The future is now", "Beyond imagination", "A new world awaits", "Discover the unknown"],
        "drama": ["A story of courage", "Love conquers all", "The truth will surface", "One life. One chance."],
        "romance": ["Love finds a way", "Two hearts. One destiny.", "A timeless love story", "Meant to be"],
        "thriller": ["Trust no one", "The truth is deadly", "Time is running out", "Every second counts"],
        "fantasy": ["Magic is real", "A legendary journey", "Believe in the impossible", "Destiny awaits"],
        "epic": ["Legends will rise", "The battle for everything", "Heroes are born", "An epic tale"],
        "comedy": ["Laugh out loud", "The funniest story ever told", "Get ready to smile", "Pure comedy gold"]
    }
    
    RATINGS = ["PG", "PG-13", "R", "NR"]
    
    ACTOR_NAMES = [
        "CHRIS EVANS", "SCARLETT JOHANSSON", "TOM HARDY", "EMMA STONE",
        "RYAN GOSLING", "MARGOT ROBBIE", "IDRIS ELBA", "ZOE SALDANA",
        "MICHAEL B. JORDAN", "FLORENCE PUGH", "TIMOTHÉE CHALAMET", "ZENDAYA"
    ]
    
    DIRECTOR_NAMES = [
        "CHRISTOPHER NOLAN", "DENIS VILLENEUVE", "GRETA GERWIG", "JORDAN PEELE",
        "TAIKA WAITITI", "RIAN JOHNSON", "JAMES GUNN", "CHLOE ZHAO"
    ]
    
    STUDIOS = ["UNIVERSAL", "PARAMOUNT", "WARNER BROS", "20TH CENTURY", "SONY PICTURES"]
    
    def __init__(self, fonts_dir="fonts/cinematic"):
        self.fonts_dir = Path(fonts_dir)
        self.available_fonts = self._scan_fonts()
        print(f"  Found {len(self.available_fonts)} fonts in {fonts_dir}")
    
    def _scan_fonts(self):
        """Scan fonts directory for .ttf and .otf files"""
        fonts = []
        if self.fonts_dir.exists():
            fonts.extend(list(self.fonts_dir.glob("*.ttf")))
            fonts.extend(list(self.fonts_dir.glob("*.otf")))
        return fonts
    
    def generate_tagline(self, keywords, genre):
        """Generate tagline from keywords or use genre template"""
        words = keywords.upper().split()
        
        if len(words) >= 3:
            return f"{words[0]} {words[1]} {words[2]}"
        
        taglines = self.GENRE_TAGLINES.get(genre, self.GENRE_TAGLINES["epic"])
        return random.choice(taglines).upper()
    
    def generate_release_date(self):
        """Generate realistic release date"""
        base = datetime.now()
        offset = random.randint(30, 365)
        release = base + timedelta(days=offset)
        
        month = release.strftime("%B").upper()
        day = release.day
        year = release.year
        
        return f"{month} {day}, {year}"
    
    def get_credits(self):
        """Generate random cast and crew"""
        actors = random.sample(self.ACTOR_NAMES, 3)
        director = random.choice(self.DIRECTOR_NAMES)
        studio = random.choice(self.STUDIOS)
        
        return {
            "actors": actors,
            "director": director,
            "studio": studio
        }
    
    def get_rating(self, genre):
        """Get appropriate rating for genre"""
        if genre in ["horror", "thriller"]:
            return random.choice(["R", "PG-13"])
        elif genre in ["action", "scifi"]:
            return "PG-13"
        else:
            return random.choice(["PG", "PG-13"])
    
    def select_random_font(self, template_name):
        """Select random font that matches template style"""
        if not self.available_fonts:
            return "arial.ttf"
        
        # Font style preferences for different templates
        bold_templates = ["wide_compressed", "ultra_wide", "extreme_wide"]
        elegant_templates = ["narrow_tall", "slight_tall"]
        
        # Categorize fonts by style
        bold_fonts = ["BebasNeueRegular.ttf", "Arvo-Bold.ttf", "Montserrat-Bold.ttf", 
                     "Blocksmith.otf", "TrajanPro-Regular.ttf", "Redhawk.otf"]
        elegant_fonts = ["PlayfairDisplay-Regular.ttf", "garamond_[allfont.ru].ttf", 
                        "CinzelDecorative-Regular.ttf", "bodoni_[allfont.net].ttf"]
        modern_fonts = ["GothamRegular-1GwDg.ttf", "Montserrat-Regular.ttf", 
                       "ShinkosansRegular-8OO50.otf", "Hexaplex.otf"]
        
        # Select based on template
        if template_name in bold_templates:
            preferred = [f for f in self.available_fonts if f.name in bold_fonts]
        elif template_name in elegant_templates:
            preferred = [f for f in self.available_fonts if f.name in elegant_fonts]
        else:
            preferred = [f for f in self.available_fonts if f.name in modern_fonts]
        
        # Fallback to any font if no match
        if not preferred:
            preferred = self.available_fonts
        
        selected = random.choice(preferred)
        print(f"    Selected font: {selected.name} for template: {template_name}")
        return str(selected)
    
    def load_font(self, size, font_path=None):
        """Load font with fallback"""
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"    Warning: Could not load {font_path}, using fallback")
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def analyze_title_region(self, image, y_pos, height):
        """Analyze background brightness in title region"""
        w, h = image.size
        crop = image.crop((0, max(0, y_pos - 20), w, min(h, y_pos + height + 20)))
        import numpy as np
        arr = np.array(crop)
        brightness = np.mean(arr)
        return brightness
    
    def get_random_template(self):
        """Get random poster template style"""
        templates = [
            {"y_pos": 0.45, "stretch_h": 1.0, "stretch_v": 1.0, "name": "centered"},
            {"y_pos": 0.65, "stretch_h": 1.3, "stretch_v": 0.9, "name": "wide_compressed"},
            {"y_pos": 0.70, "stretch_h": 0.8, "stretch_v": 1.4, "name": "narrow_tall"},
            {"y_pos": 0.55, "stretch_h": 1.5, "stretch_v": 0.8, "name": "ultra_wide"},
            {"y_pos": 0.75, "stretch_h": 1.0, "stretch_v": 1.2, "name": "tall_bottom"},
            {"y_pos": 0.40, "stretch_h": 1.2, "stretch_v": 1.0, "name": "wide_top"},
            {"y_pos": 0.68, "stretch_h": 0.9, "stretch_v": 1.1, "name": "slight_tall"},
            {"y_pos": 0.50, "stretch_h": 1.4, "stretch_v": 0.85, "name": "extreme_wide"},
        ]
        return random.choice(templates)
    
    def add_movie_poster_elements(self, image, title, genre, keywords):
        """Add complete movie poster design"""
        w, h = image.size
        img = image.copy().convert('RGBA')
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Generate content
        tagline = self.generate_tagline(keywords, genre)
        release_date = self.generate_release_date()
        credits = self.get_credits()
        
        margin = int(w * 0.05)
        
        # 1. TITLE (Random template with distortion)
        template = self.get_random_template()
        print(f"    Selected template: {template['name']} (stretch_h={template['stretch_h']}, stretch_v={template['stretch_v']})")
        
        # Select random font matching template style
        font_path = self.select_random_font(template['name'])
        
        title_size = int(h * 0.14)
        title_font = self.load_font(title_size, font_path=font_path)
        title_text = title.upper()
        
        # Create title on separate layer for distortion
        temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bbox = temp_draw.textbbox((0, 0), title_text, font=title_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Add padding for shadow and stroke
        padding = 100
        temp_w = text_w + padding * 2
        temp_h = text_h + padding * 2
        
        temp_img = Image.new('RGBA', (temp_w, temp_h), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Draw title centered in temp image
        temp_x = padding
        temp_y = padding
        
        # Analyze background for color
        title_y = int(h * template['y_pos'])
        bg_brightness = self.analyze_title_region(image, title_y, text_h)
        if bg_brightness < 128:
            title_color = (255, 255, 255)
            shadow_color = (0, 0, 0, 220)
        else:
            title_color = (0, 0, 0)
            shadow_color = (255, 255, 255, 180)
        
        # Shadow
        for i in range(10, 0, -1):
            temp_draw.text((temp_x + i, temp_y + i), title_text, font=title_font, fill=shadow_color)
        
        # Stroke and fill
        temp_draw.text((temp_x, temp_y), title_text, font=title_font, fill=shadow_color[:3], 
                      stroke_width=8, stroke_fill=shadow_color[:3])
        temp_draw.text((temp_x, temp_y), title_text, font=title_font, fill=title_color)
        
        # Apply distortion (stretch/compress)
        new_w = int(temp_img.width * template['stretch_h'])
        new_h = int(temp_img.height * template['stretch_v'])
        
        # Ensure title fits within bounds
        max_w = int(w * 0.9)
        max_h = int(h * 0.25)
        if new_w > max_w:
            scale = max_w / new_w
            new_w = max_w
            new_h = int(new_h * scale)
        if new_h > max_h:
            scale = max_h / new_h
            new_h = max_h
            new_w = int(new_w * scale)
        
        title_layer = temp_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Paste distorted title onto overlay with strict boundary check
        paste_x = (w - new_w) // 2
        if paste_x < margin:
            paste_x = margin
        if paste_x + new_w > w - margin:
            paste_x = w - new_w - margin
        
        paste_y = title_y
        if paste_y < margin:
            paste_y = margin
        if paste_y + new_h > h - int(h * 0.25):
            paste_y = h - new_h - int(h * 0.25)
        
        # Final safety check
        if paste_x >= 0 and paste_y >= 0 and paste_x + new_w <= w and paste_y + new_h <= h:
            overlay.paste(title_layer, (paste_x, paste_y), title_layer)
        else:
            print(f"    Warning: Title positioning issue, adjusting...")
            paste_x = max(0, min(paste_x, w - new_w))
            paste_y = max(0, min(paste_y, h - new_h))
            overlay.paste(title_layer, (paste_x, paste_y), title_layer)
        
        title_h = new_h
        
        # 2. RELEASE DATE (Bottom)
        date_size = int(h * 0.045)
        date_font = self.load_font(date_size, font_path=None)
        date_text = f"IN THEATERS {release_date}"
        
        bbox = draw.textbbox((0, 0), date_text, font=date_font)
        date_w = bbox[2] - bbox[0]
        date_h = bbox[3] - bbox[1]
        date_x = max(margin, min((w - date_w) // 2, w - date_w - margin))
        date_y = max(h - int(h * 0.08), h - date_h - margin * 2)
        
        if date_y + date_h < h - margin:
            for i in range(3, 0, -1):
                draw.text((date_x + i, date_y + i), date_text, font=date_font, fill=(0, 0, 0, 180))
            draw.text((date_x, date_y), date_text, font=date_font, fill=(255, 215, 0))
        
        # Composite
        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
