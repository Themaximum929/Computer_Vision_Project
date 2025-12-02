"""Train LayoutGAN on poster dataset"""
import torch
import numpy as np
import json
import glob
from pathlib import Path
from src.layout_gan import LayoutGAN
from torchvision import models, transforms
from PIL import Image

def extract_image_features(image_path):
    """Extract features from image using ResNet"""
    model = models.resnet18(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model.eval()
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    img = Image.open(image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)
    
    with torch.no_grad():
        features = model(img_tensor)
    
    return features.squeeze().numpy()

def extract_text_features(keywords):
    """Simple text embedding (can be replaced with BERT)"""
    embedding = np.zeros(256)
    words = keywords.lower().split()
    
    vocab = ['movie', 'music', 'event', 'sports', 'anime', 'cyberpunk', 'neon', 
             'love', 'action', 'concert', 'festival', 'championship']
    
    for i, word in enumerate(vocab[:12]):
        if word in words:
            embedding[i * 20:(i + 1) * 20] = 1.0
    
    embedding += np.random.randn(256) * 0.1
    return embedding

def load_training_data():
    """Load layouts from existing templates"""
    templates = glob.glob("templates/template*_layers.json")
    
    layouts = []
    conditions = []
    
    for template_file in templates:
        with open(template_file) as f:
            template = json.load(f)
        
        # Convert template to layout tensor
        layout = []
        for layer in template['layers']:
            if 'image' in layer['name'].lower():
                bbox = layer['bbox']
                # Normalize to [0, 1]
                x1, y1, x2, y2 = bbox[0]/720, bbox[1]/1080, bbox[2]/720, bbox[3]/1080
                layout.append([x1, y1, x2, y2, 1, 0, 0])  # type: image
            elif 'text' in layer['name'].lower() or 'title' in layer['name'].lower():
                bbox = layer['bbox']
                x1, y1, x2, y2 = bbox[0]/720, bbox[1]/1080, bbox[2]/720, bbox[3]/1080
                layout.append([x1, y1, x2, y2, 0, 1, 0])  # type: title
            elif 'caption' in layer['name'].lower():
                bbox = layer['bbox']
                x1, y1, x2, y2 = bbox[0]/720, bbox[1]/1080, bbox[2]/720, bbox[3]/1080
                layout.append([x1, y1, x2, y2, 0, 0, 1])  # type: caption
        
        # Pad to 3 elements
        while len(layout) < 3:
            layout.append([0, 0, 0, 0, 0, 0, 0])
        layout = layout[:3]
        
        layouts.append(layout)
        
        # Generate dummy conditions
        img_feat = np.random.randn(512)  # Match ResNet-18 output
        text_feat = extract_text_features("movie poster")
        conditions.append((img_feat, text_feat))
    
    return np.array(layouts), conditions

def train():
    """Train LayoutGAN"""
    print("=" * 60)
    print("Training LayoutGAN on Poster Templates")
    print("=" * 60)
    
    # Load data
    print("\nLoading training data...")
    layouts, conditions = load_training_data()
    print(f"Loaded {len(layouts)} template layouts")
    
    # Initialize GAN
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    gan = LayoutGAN(device=device)
    
    # Training loop with more epochs for diversity
    epochs = 1000
    batch_size = 4
    
    print(f"\nTraining for {epochs} epochs...")
    
    for epoch in range(epochs):
        # Sample batch
        indices = np.random.choice(len(layouts), batch_size, replace=True)
        batch_layouts = torch.tensor(layouts[indices], dtype=torch.float32).to(device)
        
        batch_img_feats = torch.tensor([conditions[i][0] for i in indices], dtype=torch.float32).to(device)
        batch_text_feats = torch.tensor([conditions[i][1] for i in indices], dtype=torch.float32).to(device)
        
        # Train step
        d_loss, g_loss = gan.train_step(batch_layouts, batch_img_feats, batch_text_feats)
        
        if epoch % 50 == 0:
            print(f"Epoch {epoch}/{epochs} - D_loss: {d_loss:.4f}, G_loss: {g_loss:.4f}")
    
    # Save model
    gan.save_checkpoint()
    print(f"\n✅ Training complete! Model saved to models/layout_gan.pth")
    
    # Test generation
    print("\nTesting generation...")
    test_img_feat = np.random.randn(512)
    test_text_feat = extract_text_features("cyberpunk neon city")
    
    layout = gan.generate(test_img_feat, test_text_feat)
    print(f"Generated layout shape: {layout.shape}")
    print(f"Sample element: {layout[0]}")
    print(f"\n✅ Model ready for use!")

if __name__ == "__main__":
    train()
