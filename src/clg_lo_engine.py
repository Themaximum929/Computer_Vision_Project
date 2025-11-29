"""CLG-LO Engine - Constrained LayoutGAN with Latent Optimization"""
import torch
import numpy as np
from PIL import Image
from torchvision import models, transforms
from src.layout_gan import LayoutGAN
from src.latent_optimizer import LatentOptimizer

class CLGLOEngine:
    """Complete CLG-LO system for poster layout generation"""
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.layout_gan = LayoutGAN(device=self.device)
        self.optimizer = LatentOptimizer(self.layout_gan)
        
        # Feature extractor
        self.feature_extractor = models.resnet18(pretrained=True)
        self.feature_extractor = torch.nn.Sequential(*list(self.feature_extractor.children())[:-1])
        self.feature_extractor.eval()
        self.feature_extractor.to(self.device)
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def extract_image_features(self, image):
        """Extract features from FLUX-generated image"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.feature_extractor(img_tensor)
        
        return features.squeeze().cpu().numpy()
    
    def extract_text_features(self, keywords):
        """Extract features from keywords"""
        # Simple embedding (can be enhanced with BERT)
        vocab = {
            'movie': 0, 'music': 1, 'event': 2, 'sports': 3,
            'anime': 4, 'cyberpunk': 5, 'neon': 6, 'love': 7,
            'action': 8, 'concert': 9, 'festival': 10, 'championship': 11,
            'summer': 12, 'winter': 13, 'city': 14, 'nature': 15
        }
        
        embedding = np.zeros(256)
        words = keywords.lower().split()
        
        for word in words:
            if word in vocab:
                idx = vocab[word]
                embedding[idx * 16:(idx + 1) * 16] = 1.0
        
        # Add genre-specific patterns
        if any(w in words for w in ['movie', 'film', 'cinema']):
            embedding[128:144] = 0.8
        elif any(w in words for w in ['music', 'concert', 'band']):
            embedding[144:160] = 0.8
        elif any(w in words for w in ['event', 'festival', 'party']):
            embedding[160:176] = 0.8
        
        return embedding
    
    def generate_layout(self, flux_image, keywords, optimize=True):
        """Generate optimized layout using CLG-LO"""
        print("\n[CLG-LO] Generating layout...")
        
        # Extract features
        print("  Extracting image features...")
        img_features = self.extract_image_features(flux_image)
        
        print("  Extracting text features...")
        text_features = self.extract_text_features(keywords)
        
        if optimize:
            # Use latent optimization
            print("  Running latent optimization...")
            layout, loss = self.optimizer.optimize(img_features, text_features, iterations=50)
            print(f"  Final loss: {loss:.4f}")
        else:
            # Direct generation
            print("  Generating layout...")
            layout = self.layout_gan.generate(img_features, text_features)
        
        # Convert to template format
        template = self.layout_to_template(layout)
        
        return template
    
    def layout_to_template(self, layout):
        """Convert neural network output to template format"""
        # layout shape: [num_elements, 7] -> [x1, y1, x2, y2, type_logits(3)]
        
        w, h = 720, 1080
        
        layers = [{'name': 'Background', 'bbox': [0, 0, w, h]}]
        
        for i, elem in enumerate(layout):
            x1, y1, x2, y2 = elem[:4]
            type_logits = elem[4:]
            
            # Denormalize coordinates
            bbox = [
                int(x1 * w),
                int(y1 * h),
                int(x2 * w),
                int(y2 * h)
            ]
            
            # Determine type
            type_idx = np.argmax(type_logits)
            type_names = ['Image', 'Text', 'Caption']
            
            layers.append({
                'name': type_names[type_idx],
                'bbox': bbox
            })
        
        template = {
            'size': [w, h],
            'layout_type': 'clg_lo_generated',
            'background_color': '#faefcf',
            'layers': layers,
            'fonts': {
                'title': {'family': 'Graduate-Regular.ttf', 'size': 42, 'color': '#043bb4', 'align': 'center'},
                'caption': {'family': 'Graduate-Regular.ttf', 'size': 18, 'color': '#043bb4', 'align': 'center'}
            }
        }
        
        return template
