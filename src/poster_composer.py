from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
import cv2

class PosterComposer:
    """Compose final poster by replacing image region in template with generated content"""
    
    def __init__(self, templates_dir="poster_templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = self._scan_templates()
        print(f"  Found {len(self.templates)} poster templates")
    
    def _scan_templates(self):
        """Scan templates directory for poster images"""
        templates = []
        if self.templates_dir.exists():
            templates.extend(list(self.templates_dir.glob("*.jpg")))
            templates.extend(list(self.templates_dir.glob("*.png")))
        return templates
    
    def detect_image_region(self, template_path):
        """Detect main image region in poster template using edge detection"""
        img = cv2.imread(str(template_path))
        if img is None:
            return None
        
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            # Fallback: use top 60% of poster as image region
            return {
                'x': int(w * 0.05),
                'y': int(h * 0.05),
                'width': int(w * 0.9),
                'height': int(h * 0.6)
            }
        
        # Find largest contour (likely the main image)
        largest = max(contours, key=cv2.contourArea)
        x, y, cw, ch = cv2.boundingRect(largest)
        
        # Validate region size (should be significant portion of poster)
        if cw < w * 0.3 or ch < h * 0.3:
            # Use default region
            return {
                'x': int(w * 0.05),
                'y': int(h * 0.05),
                'width': int(w * 0.9),
                'height': int(h * 0.6)
            }
        
        return {'x': x, 'y': y, 'width': cw, 'height': ch}
    
    def detect_text_regions(self, template_path):
        """Detect text regions in poster (areas to preserve)"""
        img = cv2.imread(str(template_path))
        if img is None:
            return []
        
        h, w = img.shape[:2]
        
        # Common text regions in movie posters
        regions = [
            {'name': 'title', 'y': int(h * 0.65), 'height': int(h * 0.15)},
            {'name': 'credits', 'y': int(h * 0.80), 'height': int(h * 0.15)},
            {'name': 'top_billing', 'y': 0, 'height': int(h * 0.1)}
        ]
        
        return regions
    
    def compose_poster(self, template_path, generated_image, output_path=None):
        """Compose final poster by replacing image region with generated content"""
        print(f"  Composing poster using template: {Path(template_path).name}")
        
        # Load template
        template = Image.open(template_path).convert('RGB')
        tw, th = template.size
        
        # Detect image region
        region = self.detect_image_region(template_path)
        if not region:
            print("  Warning: Could not detect image region, using full template")
            return template
        
        print(f"  Image region: x={region['x']}, y={region['y']}, w={region['width']}, h={region['height']}")
        
        # Resize generated image to fit region
        gen_img = generated_image.convert('RGB')
        gen_img_resized = gen_img.resize((region['width'], region['height']), Image.Resampling.LANCZOS)
        
        # Create composite
        result = template.copy()
        result.paste(gen_img_resized, (region['x'], region['y']))
        
        if output_path:
            result.save(output_path, quality=95)
            print(f"  Composed poster saved to: {output_path}")
        
        return result
    
    def get_random_template(self):
        """Get random template from available templates"""
        if not self.templates:
            return None
        import random
        return random.choice(self.templates)
    
    def create_simple_template(self, width=720, height=1280):
        """Create simple poster template with predefined layout"""
        template = Image.new('RGB', (width, height), (20, 20, 20))
        draw = ImageDraw.Draw(template)
        
        # Define image region (top 65%)
        img_region = {
            'x': 0,
            'y': 0,
            'width': width,
            'height': int(height * 0.65)
        }
        
        # Draw placeholder for image region
        draw.rectangle([0, 0, width, int(height * 0.65)], fill=(40, 40, 40))
        
        # Title region (middle)
        draw.rectangle([0, int(height * 0.65), width, int(height * 0.80)], fill=(20, 20, 20))
        
        # Credits region (bottom)
        draw.rectangle([0, int(height * 0.80), width, height], fill=(15, 15, 15))
        
        return template, img_region
    
    def compose_with_simple_layout(self, generated_image, output_path=None):
        """Compose poster using simple predefined layout"""
        print("  Using simple layout template")
        
        # Create template
        template, region = self.create_simple_template()
        
        # Resize generated image to fit region
        gen_img = generated_image.convert('RGB')
        gen_img_resized = gen_img.resize((region['width'], region['height']), Image.Resampling.LANCZOS)
        
        # Paste into template
        result = template.copy()
        result.paste(gen_img_resized, (region['x'], region['y']))
        
        if output_path:
            result.save(output_path, quality=95)
            print(f"  Composed poster saved to: {output_path}")
        
        return result
