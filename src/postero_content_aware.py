"""
PosterO Content-Aware Layout Generation Pipeline
Uses pre-trained design intent detection + LLM-based layout generation
"""
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import sys
import os

class PosterOContentAware:
    """Content-aware layout generation using PosterO with design intent detection"""
    
    def __init__(self, llm_path, dataset_root, intent_model_path=None, canvas_size=(720, 1080)):
        """
        Args:
            llm_path: Path to LLM (Mistral-7B or LLaMA-3.1-8B)
            dataset_root: Path to PKU/CGL dataset root
            intent_model_path: Path to pre-trained design intent model (optional)
            canvas_size: Target canvas size
        """
        self.llm_path = llm_path
        self.dataset_root = Path(dataset_root)
        self.intent_model_path = intent_model_path
        self.canvas_size = canvas_size
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load design intent detector if provided
        self.intent_detector = self._load_intent_detector() if intent_model_path else None
        
    def _load_intent_detector(self):
        """Load pre-trained design intent detection model"""
        try:
            # Import PosterO design intent detector
            sys.path.insert(0, str(self.dataset_root.parent / 'PosterO' / 'design_intent_detect'))
            from model import DesignIntentDetector
            
            model = DesignIntentDetector()
            checkpoint = torch.load(self.intent_model_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            return model
        except Exception as e:
            print(f"⚠ Failed to load intent detector: {e}")
            return None
    
    def detect_design_intent(self, image):
        """
        Detect available layout regions using design intent model
        
        Args:
            image: PIL Image or path
            
        Returns:
            List of bounding boxes [(x1, y1, x2, y2), ...]
        """
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        if self.intent_detector is None:
            # Fallback: rule-based detection
            w, h = image.size
            margin = int(min(w, h) * 0.07)
            return [(margin, margin, w - margin, h - margin)]
        
        # Use trained model
        with torch.no_grad():
            img_tensor = self._preprocess_image(image)
            bboxes = self.intent_detector(img_tensor)
            return self._postprocess_bboxes(bboxes, image.size)
    
    def _preprocess_image(self, image):
        """Preprocess image for intent detection"""
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        return transform(image).unsqueeze(0).to(self.device)
    
    def _postprocess_bboxes(self, bboxes, orig_size):
        """Convert model output to bounding boxes"""
        # Scale from normalized coords to image size
        w, h = orig_size
        return [(int(b[0]*w), int(b[1]*h), int(b[2]*w), int(b[3]*h)) for b in bboxes]
    
    def generate_layout(self, image, keywords, num_elements=3, sample_size=5):
        """
        Generate content-aware layout
        
        Args:
            image: PIL Image or path to background image
            keywords: String or list of keywords
            num_elements: Number of layout elements
            sample_size: Number of RAG samples
            
        Returns:
            dict: Layout with bboxes, labels, canvas_size
        """
        if isinstance(keywords, str):
            keywords = keywords.split()
        
        # Step 1: Detect design intent regions
        intent_bboxes = self.detect_design_intent(image)
        print(f"✓ Detected {len(intent_bboxes)} design intent regions")
        
        # Step 2: Load dataset and setup pipeline
        from src.generalized_setting.pipeline import LayoutGenerationPipeline
        
        dataset_info = self._get_dataset_info()
        
        pipeline = LayoutGenerationPipeline(
            dataset_info=dataset_info,
            strategy={'structure': 'plain', 'injection': 'top'},
            canvas_size=self.canvas_size,
            sample_size=sample_size,
            rank_strategy='random'
        )
        
        # Step 3: Generate layout using LLM
        result = pipeline.generate_layout(
            image=image,
            design_intent_bboxes=intent_bboxes,
            num_generations=1
        )
        
        layout = result['layout_graphs'][0]
        
        return {
            'bboxes': layout['box_elem'],
            'labels': layout['cls_elem'],
            'canvas_size': result['canvas_size'],
            'intent_regions': intent_bboxes
        }
    
    def _get_dataset_info(self):
        """Get dataset configuration"""
        return {
            'dataset_name': 'pku',
            'design_intent_bbox_dir': str(self.dataset_root / 'pku' / 'design_intent'),
            'annotation_dir': str(self.dataset_root / 'pku' / 'annotation'),
            'label_info': {
                1: {'type': 'text', 'color': 'green'},
                2: {'type': 'logo', 'color': 'red'},
                3: {'type': 'underlay', 'color': 'orange'}
            }
        }
    
    def layout_to_template(self, layout):
        """Convert to Key2Poster template format"""
        layers = [{'name': 'Background', 'bbox': [0, 0, *self.canvas_size]}]
        
        for i, (bbox, label) in enumerate(zip(layout['bboxes'], layout['labels'])):
            name = f"Text_{i}" if label == 1 else "Image" if label == 3 else f"Logo_{i}"
            layers.append({'name': name, 'bbox': bbox})
        
        return {
            'size': list(self.canvas_size),
            'layers': layers,
            'background_color': '#faefcf'
        }
