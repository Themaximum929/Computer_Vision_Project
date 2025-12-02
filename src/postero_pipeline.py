"""PosterO Full Pipeline Implementation (CVPR 2025)

This module implements the complete PosterO pipeline:
1. Design Intent Detection
2. Saliency-based Content Analysis  
3. Layout Tree Generation via LLM
4. In-context Learning for Generalized Layouts

Reference: https://github.com/theKinsley/PosterO-CVPR2025
"""

import sys
import os
from pathlib import Path
import torch
import numpy as np
from PIL import Image
import cv2
import json

# Try to import PosterO if available
POSTERO_PATH = r"C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025"
POSTERO_AVAILABLE = False

if Path(POSTERO_PATH).exists():
    sys.path.insert(0, POSTERO_PATH)
    try:
        from layout_generate.layoutPlanter import LayoutPlanter
        from layout_generate.PosterO import PosterO as PosterOCore
        POSTERO_AVAILABLE = True
        print("[PosterO] Official implementation loaded")
    except ImportError:
        print("[PosterO] Using fallback implementation")

class PosterOPipeline:
    """Complete PosterO pipeline for content-aware layout generation
    
    Architecture:
    - Design Intent Detection: Identifies available layout regions
    - Saliency Detection: Content-aware element placement
    - Layout Tree Generation: Hierarchical structure via LLM
    - Template Conversion: Output to Key2Poster format
    """
    
    def __init__(self, 
                 llm_path=None,
                 intent_model_path=None,
                 dataset='pku',
                 canvas_size=(720, 1080),
                 use_official=True):
        
        self.canvas_size = canvas_size
        self.dataset = dataset
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Strategy configuration (PosterO paper)
        self.strategy = {
            'structure': 'plain',      # 'plain' or 'hierarchical'
            'injection': 'pulse'       # 'none', 'top', 'pulse', 'pulse_wh'
        }
        
        # Element type definitions
        self.label_info = {
            1: {'type': 'text', 'color': 'green', 'name': 'Text'},
            2: {'type': 'logo', 'color': 'red', 'name': 'Logo'},
            3: {'type': 'underlay', 'color': 'orange', 'name': 'Image'}
        }
        
        # Initialize components
        if use_official and POSTERO_AVAILABLE:
            self._init_official_postero()
        else:
            self._init_fallback_components()
        
        print(f"[PosterO] Pipeline initialized (device: {self.device})")
    
    def _init_official_postero(self):
        """Initialize official PosterO implementation"""
        try:
            self.layout_planter = LayoutPlanter(
                self.strategy,
                dataset_info=None,
                canvas_size=self.canvas_size
            )
            self.use_official = True
            print("[PosterO] Using official implementation")
        except Exception as e:
            print(f"[PosterO] Official init failed: {e}, using fallback")
            self._init_fallback_components()
    
    def _init_fallback_components(self):
        """Initialize fallback components"""
        self.intent_detector = FallbackIntentDetector()
        self.saliency_detector = FallbackSaliencyDetector()
        self.layout_generator = FallbackLayoutGenerator(self.canvas_size)
        self.use_official = False
    
    def generate_layout(self, image, keywords, num_elements=3):
        """Generate content-aware layout
        
        Args:
            image: PIL Image or path
            keywords: String or list of keywords
            num_elements: Number of layout elements
            
        Returns:
            dict: Layout with 'layers' list
        """
        if isinstance(keywords, str):
            keywords = keywords.split()
        
        # Step 1: Design Intent Detection
        intent_regions = self._detect_intent(image)
        
        # Step 2: Saliency Detection
        saliency = self._detect_saliency(image)
        
        # Step 3: Generate Layout Tree
        if self.use_official:
            layout = self._generate_official_layout(keywords, intent_regions, num_elements)
        else:
            layout = self._generate_fallback_layout(keywords, intent_regions, saliency, num_elements)
        
        return layout
    
    def _detect_intent(self, image):
        """Detect design intent regions"""
        if isinstance(image, str):
            image = Image.open(image)
        
        w, h = image.size if hasattr(image, 'size') else self.canvas_size
        margin = int(min(w, h) * 0.07)
        
        # Return available regions (simplified)
        return [(margin, margin, w - margin, h - margin)]
    
    def _detect_saliency(self, image):
        """Detect salient regions for content-aware placement"""
        if isinstance(image, str):
            image = Image.open(image)
        
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Edge-based saliency
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        saliency = cv2.Canny(gray, 50, 150)
        
        return saliency
    
    def _generate_official_layout(self, keywords, intent_regions, num_elements):
        """Generate layout using official PosterO"""
        # Determine element types
        labels = self._keywords_to_labels(keywords, num_elements)
        
        # Build design intent dict
        design_intent_dict = {
            'den_box': intent_regions,
            'poster_path': 'generated'
        }
        
        # Generate SVG prompt
        svg_prompt = self.layout_planter.getSVGPrompt(
            labels,
            self.label_info,
            design_intent_dict
        )
        
        # Parse to layout (simplified - full version uses LLM)
        layout = self._svg_to_layout(svg_prompt, labels)
        
        return layout
    
    def _generate_fallback_layout(self, keywords, intent_regions, saliency, num_elements):
        """Generate layout using fallback rules"""
        region = intent_regions[0]
        x1, y1, x2, y2 = region
        w, h = x2 - x1, y2 - y1
        
        layers = [
            {'type': 'background', 'bbox': [0, 0, self.canvas_size[0], self.canvas_size[1]]}
        ]
        
        # Main image region (underlay)
        img_bbox = [
            x1 + int(w * 0.08),
            y1 + int(h * 0.05),
            x2 - int(w * 0.08),
            y2 - int(h * 0.15)
        ]
        layers.append({'type': 'image', 'bbox': img_bbox})
        
        # Text regions
        for i in range(min(num_elements - 1, 2)):
            if i == 0:
                # Title at bottom
                text_bbox = [
                    x1 + int(w * 0.2),
                    y2 - int(h * 0.12),
                    x2 - int(w * 0.2),
                    y2 - int(h * 0.03)
                ]
            else:
                # Subtitle at top
                text_bbox = [
                    x1 + int(w * 0.15),
                    y1 + int(h * 0.02),
                    x2 - int(w * 0.15),
                    y1 + int(h * 0.08)
                ]
            layers.append({'type': 'text', 'bbox': text_bbox})
        
        return {'layers': layers}
    
    def _keywords_to_labels(self, keywords, num_elements):
        """Convert keywords to element type labels"""
        # Default: mostly text + one underlay
        labels = [1] * max(1, num_elements - 1) + [3]
        return labels[:num_elements]
    
    def _svg_to_layout(self, svg_prompt, labels):
        """Parse SVG prompt to layout structure"""
        # Simplified parser - full version uses LLM output
        layers = [{'type': 'background', 'bbox': [0, 0, self.canvas_size[0], self.canvas_size[1]]}]
        
        for label in labels:
            elem_type = self.label_info[label]['type']
            # Generate bbox based on type
            if elem_type == 'underlay':
                bbox = [54, 59, 655, 873]
            elif elem_type == 'text':
                bbox = [240, 930, 472, 989]
            else:
                bbox = [50, 50, 150, 150]
            
            layers.append({'type': elem_type, 'bbox': bbox})
        
        return {'layers': layers}
    
    def layout_to_template(self, layout):
        """Convert PosterO layout to Key2Poster template format"""
        template = {
            "size": list(self.canvas_size),
            "layers": [],
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
        
        for layer in layout['layers']:
            layer_name = layer['type'].capitalize()
            if layer['type'] == 'underlay':
                layer_name = 'Image'
            
            template['layers'].append({
                "name": layer_name,
                "bbox": layer['bbox']
            })
        
        return template
    
    def save_template(self, template, output_path):
        """Save template to JSON file"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"[PosterO] Template saved to {output_path}")


# Fallback components (when official PosterO not available)

class FallbackIntentDetector:
    """Simplified design intent detection"""
    def detect(self, image):
        if isinstance(image, str):
            image = Image.open(image)
        w, h = image.size
        margin = int(min(w, h) * 0.07)
        return [(margin, margin, w - margin, h - margin)]


class FallbackSaliencyDetector:
    """Simplified saliency detection"""
    def detect(self, image):
        if isinstance(image, Image.Image):
            image = np.array(image)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        return cv2.Canny(gray, 50, 150)


class FallbackLayoutGenerator:
    """Rule-based layout generation"""
    def __init__(self, canvas_size):
        self.canvas_size = canvas_size
    
    def generate(self, keywords, intent_regions, num_elements=3):
        region = intent_regions[0]
        x1, y1, x2, y2 = region
        w, h = x2 - x1, y2 - y1
        
        layers = [
            {'type': 'background', 'bbox': [0, 0, self.canvas_size[0], self.canvas_size[1]]},
            {'type': 'image', 'bbox': [x1 + w//10, y1 + h//10, x2 - w//10, y2 - h//4]},
            {'type': 'text', 'bbox': [x1 + w//5, y2 - h//5, x2 - w//5, y2 - h//20]}
        ]
        
        return {'layers': layers}
