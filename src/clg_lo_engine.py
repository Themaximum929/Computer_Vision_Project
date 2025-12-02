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
            
            # Clamp to [0, 1] and ensure x2 > x1, y2 > y1
            x1 = np.clip(x1, 0, 1)
            y1 = np.clip(y1, 0, 1)
            x2 = np.clip(x2, 0, 1)
            y2 = np.clip(y2, 0, 1)
            
            if x2 <= x1:
                x2 = min(x1 + 0.1, 1.0)
            if y2 <= y1:
                y2 = min(y1 + 0.1, 1.0)
            
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
        
        import random
        
        # Random font selection
        fonts = ['Graduate-Regular.ttf', 'Montserrat-Regular.ttf', 'Lato-Bold.ttf', 
                 'PlayfairDisplay-Regular.ttf', 'IBMPlexSerif-Regular.ttf', 'Banshee-Regular.otf']
        title_font = random.choice(fonts)
        caption_font = random.choice(fonts)
        
        # Random colors
        colors = ['#043bb4', '#000000', '#ffffff', '#ff4444', '#00ff9f', '#ffd700']
        bg_colors = ['#faefcf', '#1a1a2e', '#ffffff', '#0f0f23', '#fff4e1']
        text_color = random.choice(colors)
        bg_color = random.choice(bg_colors)
        
        # Random alignment
        aligns = ['left', 'center', 'right']
        align = random.choice(aligns)
        
        template = {
            'size': [w, h],
            'layout_type': 'clg_lo_generated',
            'background_color': bg_color,
            'layers': layers,
            'fonts': {
                'title': {'family': title_font, 'size': random.randint(35, 50), 'color': text_color, 'align': align},
                'caption': {'family': caption_font, 'size': random.randint(16, 22), 'color': text_color, 'align': align}
            }
        }
        
        return template
