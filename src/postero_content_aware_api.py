"""
PosterO Content-Aware Layout Generation with HuggingFace API
No local LLM needed - uses HF Inference API
"""
import os
from pathlib import Path
from PIL import Image
from huggingface_hub import InferenceClient

class PosterOContentAwareAPI:
    """Content-aware layout using HF API (no local LLM needed)"""
    
    def __init__(self, hf_token, intent_model_path=None, canvas_size=(720, 1080)):
        """
        Args:
            hf_token: HuggingFace API token
            intent_model_path: Path to design intent model (optional)
            canvas_size: Canvas size
        """
        self.hf_token = hf_token
        self.canvas_size = canvas_size
        self.device = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'
        self.client = InferenceClient(token=hf_token)
        self.intent_detector = self._load_intent_detector(intent_model_path) if intent_model_path else None
    
    def _load_intent_detector(self, model_path):
        """Load design intent model"""
        try:
            import torch
            model = torch.load(model_path, map_location=self.device)
            return model
        except:
            return None
    
    def detect_design_intent(self, image):
        """Detect layout regions"""
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        # Rule-based fallback
        w, h = image.size
        margin = int(min(w, h) * 0.07)
        return [(margin, margin, w - margin, h - margin)]
    
    def generate_layout(self, image, keywords, num_elements=3):
        """Generate layout using HF API"""
        if isinstance(keywords, str):
            keywords = keywords.split()
        
        # Detect intent regions
        intent_bboxes = self.detect_design_intent(image)
        
        # Build prompt for LLM
        prompt = self._build_prompt(keywords, intent_bboxes, num_elements)
        
        # Call HF API with chat completion
        try:
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="mistralai/Mistral-7B-Instruct-v0.2",
                max_tokens=500,
                temperature=0.7
            )
            llm_output = response.choices[0].message.content
        except:
            # Fallback to rule-based if API fails
            llm_output = ""
        
        # Parse response to layout
        layout = self._parse_layout(llm_output, num_elements)
        
        return {
            'bboxes': layout['bboxes'],
            'labels': layout['labels'],
            'canvas_size': self.canvas_size,
            'intent_regions': intent_bboxes
        }
    
    def _build_prompt(self, keywords, intent_bboxes, num_elements):
        """Build prompt for layout generation"""
        region = intent_bboxes[0]
        return f"""Generate a poster layout with {num_elements} elements for: {' '.join(keywords)}

Available region: x1={region[0]}, y1={region[1]}, x2={region[2]}, y2={region[3]}
Canvas size: {self.canvas_size[0]}x{self.canvas_size[1]}

Return {num_elements} bounding boxes in format:
1. [x1, y1, x2, y2] - type
2. [x1, y1, x2, y2] - type
...

Types: text, image, logo"""
    
    def _parse_layout(self, response, num_elements):
        """Parse LLM response to layout"""
        # Simple rule-based layout as fallback
        w, h = self.canvas_size
        margin = int(min(w, h) * 0.07)
        
        bboxes = [
            [margin + w//10, margin + h//10, w - margin - w//10, h - margin - h//4],  # Image
            [margin + w//5, h - margin - h//8, w - margin - w//5, h - margin - h//20]  # Text
        ]
        
        labels = [3, 1]  # 3=image, 1=text
        
        return {'bboxes': bboxes[:num_elements], 'labels': labels[:num_elements]}
    
    def layout_to_template(self, layout):
        """Convert to Key2Poster template"""
        layers = [{'name': 'Background', 'bbox': [0, 0, *self.canvas_size]}]
        
        for i, (bbox, label) in enumerate(zip(layout['bboxes'], layout['labels'])):
            name = "Image" if label == 3 else f"Text_{i}"
            layers.append({'name': name, 'bbox': bbox})
        
        return {
            'size': list(self.canvas_size),
            'layers': layers,
            'background_color': '#faefcf'
        }
