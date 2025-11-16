"""Template Manager for Dynamic Poster Layouts"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json

class TemplateManager:
    def __init__(self, templates_dir="poster_templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load available templates"""
        return {
            "minimal": {"title_pos": (0.5, 0.85), "title_size": 0.08, "layout": "center"},
            "classic": {"title_pos": (0.5, 0.9), "title_size": 0.06, "layout": "bottom"},
            "modern": {"title_pos": (0.1, 0.1), "title_size": 0.05, "layout": "top-left"},
            "split": {"title_pos": (0.5, 0.5), "title_size": 0.07, "layout": "center-split"}
        }
    
    def apply_template(self, image, template_name="minimal", title="", metadata=None):
        """Apply template layout to image"""
        if template_name not in self.templates:
            template_name = "minimal"
        
        template = self.templates[template_name]
        w, h = image.size
        canvas = image.copy()
        draw = ImageDraw.Draw(canvas)
        
        # Add gradient overlay for text readability
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        if template["layout"] == "bottom":
            overlay_draw.rectangle([(0, h*0.75), (w, h)], fill=(0, 0, 0, 120))
        elif template["layout"] == "center":
            overlay_draw.rectangle([(0, h*0.4), (w, h*0.6)], fill=(0, 0, 0, 100))
        
        canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB')
        
        return canvas
    
    def get_template_list(self):
        """Return available templates"""
        return list(self.templates.keys())
