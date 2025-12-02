"""PosterO Adapter - Modern Layout Generation for Key2Poster"""
import sys
import os
sys.path.insert(0, r"C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025")

from layout_generate.layoutPlanter import LayoutPlanter
from layout_generate.PosterO import PosterO
import torch
import numpy as np
from PIL import Image

class PosterOAdapter:
    """Adapter to use PosterO for layout generation in Key2Poster pipeline"""
    
    def __init__(self, canvas_size=(720, 1080), dataset='pku'):
        self.canvas_size = canvas_size
        
        # PosterO strategy configuration
        self.strategy = {
            'structure': 'plain',  # or 'hierarchical'
            'injection': 'pulse'   # 'none', 'top', 'pulse', 'pulse_wh'
        }
        
        # Label info for poster elements
        self.label_info = {
            1: {'type': 'text', 'color': 'green'}, 
            2: {'type': 'logo', 'color': 'red'},
            3: {'type': 'underlay', 'color': 'orange'}
        }
        
        # Initialize LayoutPlanter without dataset (for inference only)
        self.layout_planter = LayoutPlanter(
            self.strategy, 
            dataset_info=None,
            canvas_size=canvas_size
        )
    
    def generate_layout(self, image, keywords, design_intent_bbox=None):
        """Generate layout using PosterO
        
        Args:
            image: PIL Image of generated poster content
            keywords: List of keywords or string
            design_intent_bbox: Optional list of available regions [(x1,y1,x2,y2), ...]
        
        Returns:
            dict: Layout with 'cls_elem' (element types) and 'box_elem' (bboxes)
        """
        if isinstance(keywords, str):
            keywords = keywords.split()
        
        # Create design intent dict
        if design_intent_bbox is None:
            # Default: use full canvas with margins
            margin = 50
            design_intent_bbox = [(margin, margin, 
                                  self.canvas_size[0]-margin, 
                                  self.canvas_size[1]-margin)]
        
        design_intent_dict = {
            'den_box': design_intent_bbox,
            'poster_path': 'generated'
        }
        
        # Generate SVG prompt for layout
        # Randomly select element types based on keywords
        num_elements = min(len(keywords), 3)
        labels = [1] * max(1, num_elements - 1) + [3]  # text + underlay
        
        svg_prompt = self.layout_planter.getSVGPrompt(
            labels, 
            self.label_info, 
            design_intent_dict
        )
        
        # For now, generate rule-based layout
        # TODO: Integrate with LLM for PosterO full pipeline
        layout = self._generate_rule_based_layout(labels, design_intent_bbox)
        
        return layout
    
    def _generate_rule_based_layout(self, labels, available_regions):
        """Generate layout using rules (fallback without LLM)"""
        cls_elem = []
        box_elem = []
        
        # Use first available region
        region = available_regions[0]
        x1, y1, x2, y2 = region
        w, h = x2 - x1, y2 - y1
        
        for i, label in enumerate(labels):
            if self.label_info[label]['type'] == 'underlay':
                # Underlay covers most of the region
                bbox = [x1 + w//10, y1 + h//10, x2 - w//10, y2 - h//10]
            elif self.label_info[label]['type'] == 'text':
                # Text in upper or lower portion
                if i == 0:
                    bbox = [x1 + w//4, y1 + h//10, x2 - w//4, y1 + h//3]
                else:
                    bbox = [x1 + w//4, y2 - h//3, x2 - w//4, y2 - h//10]
            else:  # logo
                bbox = [x1 + w//20, y1 + h//20, x1 + w//5, y1 + h//5]
            
            cls_elem.append(self.label_info[label]['type'])
            box_elem.append(bbox)
        
        return {'cls_elem': cls_elem, 'box_elem': box_elem}
    
    def layout_to_template(self, layout):
        """Convert PosterO layout to Key2Poster template format
        
        Args:
            layout: dict with 'cls_elem' and 'box_elem'
        
        Returns:
            dict: Template in Key2Poster format
        """
        layers = [
            {
                "name": "Background",
                "bbox": [0, 0, self.canvas_size[0], self.canvas_size[1]]
            }
        ]
        
        for i, (cls, bbox) in enumerate(zip(layout['cls_elem'], layout['box_elem'])):
            layer_name = f"{cls.capitalize()}_{i+1}"
            if cls == 'text':
                layer_name = f"Text_{i+1}"
            elif cls == 'underlay':
                layer_name = "Image"  # Main image region
            elif cls == 'logo':
                layer_name = "Logo"
            
            layers.append({
                "name": layer_name,
                "bbox": bbox
            })
        
        template = {
            "size": list(self.canvas_size),
            "layers": layers,
            "background_color": "#faefcf",
            "fonts": {
                "title": {
                    "family": "Graduate-Regular.ttf",
                    "size": 48,
                    "color": "#043bb4",
                    "align": "center"
                }
            }
        }
        
        return template
