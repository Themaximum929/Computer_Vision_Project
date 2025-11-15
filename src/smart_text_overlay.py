"""Smart text overlay with intelligent positioning and styling"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import cv2
from src.poster_text_styles import POSTER_STYLES

class SmartTextOverlay:
    def __init__(self):
        self.styles = POSTER_STYLES
    
    def add_title(self, image, title, genre=None, style="cinematic"):
        """Add professionally positioned and styled title"""
        # Use genre style if provided
        if genre and genre.lower() in self.styles:
            style_config = self.styles[genre.lower()]
        elif style in self.styles:
            style_config = self.styles[style]
        else:
            style_config = self.styles["cinematic"]
        
        # Analyze image to find best text position
        position_info = self._analyze_image_for_text(image)
        
        # Choose best position based on analysis
        best_position = self._choose_best_position(position_info, style_config)
        
        # Apply text with professional styling
        result = self._apply_professional_text(
            image, title, style_config, best_position
        )
        
        return result
    
    def _analyze_image_for_text(self, image):
        """Analyze image to find optimal text placement areas"""
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Divide image into regions
        regions = {
            'top': gray[0:height//3, :],
            'middle': gray[height//3:2*height//3, :],
            'bottom': gray[2*height//3:, :],
            'top_left': gray[0:height//3, 0:width//2],
            'top_right': gray[0:height//3, width//2:],
            'bottom_left': gray[2*height//3:, 0:width//2],
            'bottom_right': gray[2*height//3:, width//2:]
        }
        
        # Analyze each region
        analysis = {}
        for region_name, region_img in regions.items():
            # Calculate metrics
            brightness = np.mean(region_img)
            contrast = np.std(region_img)
            edges = cv2.Canny(region_img, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Score for text placement (prefer low edge density, moderate brightness)
            score = 0
            if 40 < brightness < 200:  # Good contrast range
                score += 30
            if edge_density < 0.1:  # Low detail area
                score += 40
            if contrast < 50:  # Uniform area
                score += 30
            
            analysis[region_name] = {
                'brightness': brightness,
                'contrast': contrast,
                'edge_density': edge_density,
                'score': score
            }
        
        return analysis
    
    def _choose_best_position(self, analysis, style_config):
        """Choose best position based on image analysis and style"""
        preferred = style_config.get('position', 'bottom')
        
        # Map style preference to regions
        region_map = {
            'top': ['top', 'top_left', 'top_right'],
            'center': ['middle'],
            'bottom': ['bottom', 'bottom_left', 'bottom_right']
        }
        
        # Get candidate regions
        candidates = region_map.get(preferred, ['bottom'])
        
        # Find best scoring region
        best_region = max(candidates, key=lambda r: analysis.get(r, {}).get('score', 0))
        best_score = analysis.get(best_region, {}).get('score', 0)
        
        # If score is too low, try other positions
        if best_score < 50:
            all_regions = ['top', 'middle', 'bottom', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
            best_region = max(all_regions, key=lambda r: analysis.get(r, {}).get('score', 0))
        
        return {
            'region': best_region,
            'brightness': analysis[best_region]['brightness'],
            'score': analysis[best_region]['score']
        }
    
    def _apply_professional_text(self, image, title, style_config, position_info):
        """Apply text with professional movie poster styling"""
        img = image.convert('RGBA')
        width, height = img.size
        
        # Create overlay layer
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Prepare title text
        title_upper = title.upper()
        
        # Auto-fit font size to poster width
        font, font_size = self._auto_fit_font(
            title_upper, width, height, style_config
        )
        
        # Calculate text position based on region
        x, y = self._calculate_smart_position(
            img, title_upper, font, position_info['region'], style_config
        )
        
        # Adjust text color based on background brightness
        text_color = self._adjust_color_for_background(
            style_config['color'], position_info['brightness']
        )
        
        # Add background bar for better readability (optional)
        if position_info['score'] < 60:
            self._add_text_background(draw, title_upper, font, x, y, width, height)
        
        # Draw shadow (multiple layers for depth)
        shadow_offset = style_config['shadow_offset']
        shadow_color = style_config['shadow_color']
        for offset in range(shadow_offset, 0, -1):
            alpha = int(shadow_color[3] * (offset / shadow_offset))
            draw.text((x + offset, y + offset), title_upper, font=font, 
                     fill=(*shadow_color[:3], alpha))
        
        # Draw stroke/outline
        if style_config['stroke_width'] > 0:
            stroke_width = style_config['stroke_width']
            stroke_color = style_config['stroke_color']
            draw.text((x, y), title_upper, font=font, fill=stroke_color,
                     stroke_width=stroke_width, stroke_fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), title_upper, font=font, fill=text_color)
        
        # Composite overlay
        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
    
    def _calculate_smart_position(self, image, text, font, region, style_config):
        """Calculate smart text position based on region"""
        width, height = image.size
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center horizontally
        x = (width - text_width) // 2
        
        # Position vertically based on region
        if 'top' in region:
            y = int(height * 0.08)
        elif 'middle' in region:
            y = (height - text_height) // 2
        else:  # bottom
            y = height - text_height - int(height * 0.10)
        
        return x, y
    
    def _adjust_color_for_background(self, color, brightness):
        """Adjust text color for optimal contrast"""
        # If background is dark, use light text
        if brightness < 100:
            return (255, 255, 255)
        # If background is light, use dark text
        elif brightness > 180:
            return (0, 0, 0)
        # Otherwise use original color
        return color
    
    def _add_text_background(self, draw, text, font, x, y, width, height):
        """Add semi-transparent background bar for text"""
        bbox = draw.textbbox((x, y), text, font=font)
        padding = 20
        
        # Draw background rectangle
        draw.rectangle(
            [0, bbox[1] - padding, width, bbox[3] + padding],
            fill=(0, 0, 0, 150)
        )
    
    def _load_font(self, font_name, fallback_name, size):
        """Load font with fallback"""
        # Try poster fonts first
        poster_fonts = ['impact.ttf', 'IMPACT.TTF', 'arialbd.ttf', 'ARIALBD.TTF']
        
        for pf in poster_fonts:
            try:
                return ImageFont.truetype(pf, size)
            except:
                pass
        
        # Try specified fonts
        try:
            return ImageFont.truetype(font_name, size)
        except:
            try:
                return ImageFont.truetype(fallback_name, size)
            except:
                return ImageFont.load_default()
    
    def _auto_fit_font(self, text, max_width, max_height, style_config):
        """Auto-fit font size to poster width with word wrapping"""
        # Start with desired size
        font_size = int(max_height * style_config['size_ratio'])
        max_text_width = int(max_width * 0.9)  # 90% of poster width
        
        # Try decreasing font sizes until text fits
        for size in range(font_size, 20, -5):
            font = self._load_font(style_config['font'], style_config['fallback'], size)
            
            # Check if text fits in one line
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_text_width:
                return font, size
        
        # If still too wide, split into multiple lines
        words = text.split()
        if len(words) > 1:
            # Try 2 lines
            mid = len(words) // 2
            line1 = ' '.join(words[:mid])
            line2 = ' '.join(words[mid:])
            
            for size in range(font_size, 20, -5):
                font = self._load_font(style_config['font'], style_config['fallback'], size)
                temp_img = Image.new('RGB', (1, 1))
                draw = ImageDraw.Draw(temp_img)
                
                bbox1 = draw.textbbox((0, 0), line1, font=font)
                bbox2 = draw.textbbox((0, 0), line2, font=font)
                w1 = bbox1[2] - bbox1[0]
                w2 = bbox2[2] - bbox2[0]
                
                if w1 <= max_text_width and w2 <= max_text_width:
                    # Return multi-line text
                    return font, size
        
        # Fallback: use smallest readable size
        font = self._load_font(style_config['font'], style_config['fallback'], 30)
        return font, 30
