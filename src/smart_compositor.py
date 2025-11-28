"""Smart Compositor - AI-driven image placement and background generation"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from src.ai_layout_generator import AILayoutGenerator
from src.clg_lo_layout import CLGLOGenerator
import cv2

class SmartCompositor:
    """Intelligent poster composition with CLG-LO layout"""
    
    def __init__(self, poster_size=(720, 1080), use_clg_lo=True):
        self.poster_size = poster_size
        self.use_clg_lo = use_clg_lo
        if use_clg_lo:
            self.layout_gen = CLGLOGenerator(poster_size)
        else:
            self.layout_gen = AILayoutGenerator(poster_size)
    
    def compose_poster(self, flux_image, title, captions, keywords, seed=None):
        """Main composition pipeline with CLG-LO"""
        if seed:
            np.random.seed(seed)
        
        # Step 1: Resize FLUX image to 1920x1080 for subject detection
        large_img = flux_image.resize((1920, 1080), Image.LANCZOS)
        
        # Step 2: Detect subject and apply composition rule
        subject_bbox = self._detect_subject(large_img)
        offset_x, offset_y = self._apply_composition(subject_bbox, (1920, 1080))
        
        # Step 3: Crop and resize to poster size with composition offset
        crop_x = max(0, min(1920 - self.poster_size[0], 
                           (1920 - self.poster_size[0])//2 - offset_x))
        crop_y = max(0, min(1080 - self.poster_size[1], 
                           (1080 - self.poster_size[1])//2 - offset_y))
        
        composed_img = large_img.crop((crop_x, crop_y, 
                                       crop_x + self.poster_size[0],
                                       crop_y + self.poster_size[1]))
        
        # Step 4: Generate background color from image mean
        img_array = np.array(composed_img)
        bg_color = tuple(img_array.mean(axis=(0, 1)).astype(int))
        
        # Step 5: Create poster with background
        poster = Image.new('RGB', self.poster_size, bg_color)
        
        # Calculate image placement (centered with slight offset for visual interest)
        img_w, img_h = composed_img.size
        paste_x = (self.poster_size[0] - img_w) // 2
        paste_y = (self.poster_size[1] - img_h) // 2
        
        # Paste image (it may not cover full poster, showing background)
        poster.paste(composed_img, (paste_x, paste_y))
        img_bbox = [paste_x, paste_y, paste_x + img_w, paste_y + img_h]
        
        # Step 6: Generate CLG-LO layout for text
        if self.use_clg_lo:
            text_layouts = self.layout_gen.generate_layout(img_bbox, title, captions, seed)
        else:
            text_layouts = self.layout_gen.generate_text_layout(poster, img_bbox, title, captions)
        
        # Step 7: Render text
        draw = ImageDraw.Draw(poster)
        for layout in text_layouts:
            self._render_text(draw, poster, layout)
        
        return poster, {
            'bg_color': '#{:02x}{:02x}{:02x}'.format(*bg_color),
            'img_bbox': img_bbox,
            'text_layouts': text_layouts,
            'composition_offset': (offset_x, offset_y)
        }
    
    def _render_text(self, draw, poster, layout):
        """Render single text element"""
        try:
            font = ImageFont.truetype(f"fonts/{layout['font']}", layout['size'])
        except:
            font = ImageFont.load_default()
        
        text = layout['text']
        x, y = layout['x'], layout['y']
        align = layout['align']
        color = layout['color'] if isinstance(layout['color'], tuple) else (255, 255, 255)
        
        # Get text bbox for positioning
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Adjust position based on alignment
        if align == 'center':
            x = x - text_w // 2
        elif align == 'right':
            x = x - text_w
        
        y = y - text_h // 2  # Vertical center
        
        # Draw text with outline
        for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0))
        draw.text((x, y), text, font=font, fill=color)
    
    def _detect_subject(self, image):
        """Detect main subject using saliency"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        _, saliency_map = saliency.computeSaliency(img_array)
        saliency_map = (saliency_map * 255).astype("uint8")
        _, thresh = cv2.threshold(saliency_map, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return (x, y, x+w, y+h)
        return (image.width//4, image.height//4, 3*image.width//4, 3*image.height//4)
    
    def _apply_composition(self, subject_bbox, img_size):
        """Apply golden ratio or rule of thirds"""
        x1, y1, x2, y2 = subject_bbox
        w, h = img_size
        cx, cy = (x1+x2)//2, (y1+y2)//2
        rule = np.random.choice(['golden', 'thirds'])
        if rule == 'golden':
            target_x, target_y = int(w * 0.618), int(h * 0.618)
        else:
            target_x = w // 3 if cx < w//2 else 2*w//3
            target_y = h // 3 if cy < h//2 else 2*h//3
        return target_x - cx, target_y - cy
