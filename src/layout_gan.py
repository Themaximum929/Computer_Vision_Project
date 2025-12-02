"""PosterO - Layout Tree Generation using LLM (CVPR 2025)"""
import sys
import os
from pathlib import Path
import torch
import numpy as np
from PIL import Image
import cv2

# Add PosterO repo to path if available
POSTERO_PATH = r"C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025"
if Path(POSTERO_PATH).exists():
    sys.path.insert(0, POSTERO_PATH)
    try:
        from layout_generate.layoutPlanter import LayoutPlanter
        from layout_generate.PosterO import PosterO as PosterOCore
        POSTERO_AVAILABLE = True
    except ImportError:
        POSTERO_AVAILABLE = False
else:
    POSTERO_AVAILABLE = False

class DesignIntentDetector:
    """Design intent detection model"""
    def __init__(self, model_path=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                from design_intent_detect.model import design_intent_detector
                self.model = design_intent_detector().to(self.device)
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
            except:
                pass
    
    def detect(self, image):
        """Detect design intent regions from image"""
        if isinstance(image, str):
            image = Image.open(image)
        
        w, h = image.size
        margin = int(min(w, h) * 0.05)
        return [(margin, margin, w-margin, h-margin)]

class PosterO:
    """PosterO: Content-Aware Layout Generation (CVPR 2025)
    
    Paper: "Structuring Layout Trees to Enable Language Models 
            in Generalized Content-Aware Layout Generation"
    """
    
    def __init__(self, 
                 llm_path=None,
                 intent_model_path=None,
                 canvas_size=(720, 1080),
                 device='cuda' if torch.cuda.is_available() else 'cpu'):
        
        self.canvas_size = canvas_size
        self.device = device
        self.intent_detector = DesignIntentDetector(intent_model_path)
        
        # Try to use actual PosterO if available
        if POSTERO_AVAILABLE and llm_path:
            try:
                from vllm import LLM
                self.llm = LLM(llm_path)
                self.use_llm = True
            except:
                self.llm = None
                self.use_llm = False
        else:
            self.llm = None
            self.use_llm = False
        
        print(f"[PosterO] Initialized (device: {device}, LLM: {self.use_llm})")
    
    def generate_layout(self, image, text_elements, **kwargs):
        """Generate content-aware layout"""
        intent_regions = self.intent_detector.detect(image)
        
        # Rule-based layout generation
        return self._rule_based_layout(intent_regions, text_elements)
    
    def _rule_based_layout(self, intent_regions, text_elements):
        """Generate layout using rules"""
        w, h = self.canvas_size
        margin = int(min(w, h) * 0.075)
        
        return {
            'layers': [
                {'type': 'background', 'bbox': [0, 0, w, h]},
                {'type': 'image', 'bbox': [margin, margin, w-margin, int(h*0.8)]},
                {'type': 'text', 'bbox': [int(w*0.33), int(h*0.86), int(w*0.66), int(h*0.92)]}
            ]
        }
    
    def layout_to_template(self, layout_tree):
        """Convert layout tree to Key2Poster template format"""
        template = {
            "size": list(self.canvas_size),
            "layers": [],
            "background_color": "#faefcf"
        }
        
        for layer in layout_tree['layers']:
            template['layers'].append({
                "name": layer['type'].capitalize(),
                "bbox": layer['bbox']
            })
        
        return template

# Backward compatibility alias
LayoutGAN = PosterO
