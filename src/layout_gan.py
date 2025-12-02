"""LayoutGAN - Neural Network for Poster Layout Generation"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
import json

class Generator(nn.Module):
    """Generator: noise + conditions -> layout"""
    def __init__(self, noise_dim=128, img_feat_dim=512, text_feat_dim=256, num_elements=3):
        super().__init__()
        self.num_elements = num_elements
        
        # Input: [noise(128) + image_features(512) + text_embedding(256)] = 896
        input_dim = noise_dim + img_feat_dim + text_feat_dim
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            
            nn.Linear(512, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            
            # Output: [x1, y1, x2, y2, type_logits(3)] * num_elements
            nn.Linear(256, num_elements * 7),
            nn.Sigmoid()  # Normalize to [0, 1]
        )
    
    def forward(self, noise, img_features, text_features):
        x = torch.cat([noise, img_features, text_features], dim=1)
        output = self.model(x)
        return output.view(-1, self.num_elements, 7)

class Discriminator(nn.Module):
    """Discriminator: layout -> real/fake"""
    def __init__(self, num_elements=3):
        super().__init__()
        
        # Input: [x1, y1, x2, y2, type(3)] * num_elements = 21
        input_dim = num_elements * 7
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, layout):
        x = layout.view(layout.size(0), -1)
        return self.model(x)

class LayoutGAN:
    """Complete LayoutGAN system"""
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.generator = Generator().to(device)
        self.discriminator = Discriminator().to(device)
        
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        self.criterion = nn.BCELoss()
        
        # Load pretrained if exists
        self.load_checkpoint()
    
    def train_step(self, real_layouts, img_features, text_features):
        """Single training step with diversity enforcement"""
        batch_size = real_layouts.size(0)
        
        # Labels with label smoothing
        real_labels = torch.ones(batch_size, 1).to(self.device) * 0.9
        fake_labels = torch.zeros(batch_size, 1).to(self.device) + 0.1
        
        # Train Discriminator
        self.d_optimizer.zero_grad()
        
        # Real layouts
        real_output = self.discriminator(real_layouts)
        d_loss_real = self.criterion(real_output, real_labels)
        
        # Fake layouts with DIVERSE noise
        noise = torch.randn(batch_size, 128).to(self.device)
        fake_layouts = self.generator(noise, img_features, text_features)
        fake_output = self.discriminator(fake_layouts.detach())
        d_loss_fake = self.criterion(fake_output, fake_labels)
        
        d_loss = d_loss_real + d_loss_fake
        d_loss.backward()
        self.d_optimizer.step()
        
        # Train Generator with diversity loss
        self.g_optimizer.zero_grad()
        
        # Generate multiple layouts
        noise1 = torch.randn(batch_size, 128).to(self.device)
        noise2 = torch.randn(batch_size, 128).to(self.device)
        
        fake_layouts1 = self.generator(noise1, img_features, text_features)
        fake_layouts2 = self.generator(noise2, img_features, text_features)
        
        # Adversarial loss
        fake_output = self.discriminator(fake_layouts1)
        g_loss_adv = self.criterion(fake_output, torch.ones(batch_size, 1).to(self.device))
        
        # Diversity loss: different noise should produce different layouts
        diversity_loss = -torch.mean(torch.abs(fake_layouts1 - fake_layouts2))
        
        g_loss = g_loss_adv + 0.1 * diversity_loss
        
        g_loss.backward()
        self.g_optimizer.step()
        
        return d_loss.item(), g_loss.item()
    
    def generate(self, img_features, text_features, noise=None):
        """Generate layout from conditions"""
        self.generator.eval()
        
        with torch.no_grad():
            if noise is None:
                noise = torch.randn(1, 128).to(self.device)
            
            if not isinstance(img_features, torch.Tensor):
                img_features = torch.tensor(img_features, dtype=torch.float32).unsqueeze(0).to(self.device)
            if not isinstance(text_features, torch.Tensor):
                text_features = torch.tensor(text_features, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            layout = self.generator(noise, img_features, text_features)
        
        return layout.cpu().numpy()[0]
    
    def save_checkpoint(self, path='models/layout_gan.pth'):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'generator': self.generator.state_dict(),
            'discriminator': self.discriminator.state_dict(),
            'g_optimizer': self.g_optimizer.state_dict(),
            'd_optimizer': self.d_optimizer.state_dict(),
        }, path)
    
    def load_checkpoint(self, path='models/layout_gan.pth'):
        if Path(path).exists():
            checkpoint = torch.load(path, map_location=self.device)
            self.generator.load_state_dict(checkpoint['generator'])
            self.discriminator.load_state_dict(checkpoint['discriminator'])
            self.g_optimizer.load_state_dict(checkpoint['g_optimizer'])
            self.d_optimizer.load_state_dict(checkpoint['d_optimizer'])
            print(f"Loaded LayoutGAN checkpoint from {path}")
            return True
        return False
