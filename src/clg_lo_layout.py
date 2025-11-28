"""CLG-LO: Constrained Layout Generation with Latent Optimization"""
import torch
import torch.nn as nn
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

class LayoutGAN(nn.Module):
    """Lightweight LayoutGAN for poster generation"""
    def __init__(self, latent_dim=128, output_dim=10):
        super().__init__()
        self.gen = nn.Sequential(
            nn.Linear(latent_dim, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, output_dim), nn.Sigmoid()
        )
    
    def forward(self, z):
        return self.gen(z)

class ConstraintLoss:
    """Rule-based constraint losses"""
    @staticmethod
    def overlap_loss(boxes):
        """IoU < 0.1 constraint"""
        loss = 0
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                iou = ConstraintLoss._compute_iou(boxes[i], boxes[j])
                loss += max(0, iou - 0.1)
        return loss
    
    @staticmethod
    def _compute_iou(box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2-x1) * max(0, y2-y1)
        area1 = (box1[2]-box1[0]) * (box1[3]-box1[1])
        area2 = (box2[2]-box2[0]) * (box2[3]-box2[1])
        return inter / (area1 + area2 - inter + 1e-6)
    
    @staticmethod
    def alignment_loss(boxes, grid_size=10):
        """Grid alignment constraint"""
        loss = 0
        for box in boxes:
            for coord in box:
                loss += min(coord % grid_size, grid_size - coord % grid_size)
        return loss / (len(boxes) * 4 * grid_size)
    
    @staticmethod
    def hierarchy_loss(title_box, caption_boxes):
        """Title at top, captions below"""
        loss = 0
        for cap in caption_boxes:
            loss += max(0, title_box[1] - cap[1])  # Title y < caption y
        return loss
    
    @staticmethod
    def border_loss(boxes, W, H, border=50):
        """50px border constraint"""
        loss = 0
        for box in boxes:
            loss += max(0, border - box[0])  # Left
            loss += max(0, border - box[1])  # Top
            loss += max(0, box[2] - (W - border))  # Right
            loss += max(0, box[3] - (H - border))  # Bottom
        return loss / len(boxes)
    
    @staticmethod
    def balance_loss(boxes, W, H):
        """Visual balance via coverage"""
        coverage = sum((b[2]-b[0])*(b[3]-b[1]) for b in boxes) / (W*H)
        return abs(coverage - 0.3)  # Target 30% coverage

class CLGLOGenerator:
    """CLG-LO: LayoutGAN + Latent Optimization"""
    def __init__(self, poster_size=(720, 1080)):
        self.W, self.H = poster_size
        self.gan = LayoutGAN()
        self.gan.eval()
        self.fonts = ['Graduate-Regular.ttf', 'Montserrat-Regular.ttf', 'Lato-Bold.ttf']
    
    def generate_layout(self, img_bbox, title, captions, seed=None):
        """Generate layout with constraint optimization"""
        if seed:
            torch.manual_seed(seed)
            np.random.seed(seed)
        
        # Initial latent code
        z = torch.randn(1, 128, requires_grad=True)
        optimizer = torch.optim.Adam([z], lr=0.1)
        
        # Latent optimization loop
        for _ in range(50):
            optimizer.zero_grad()
            layout_params = self.gan(z)[0]
            
            # Decode to boxes
            title_box, cap_boxes = self._decode_layout(layout_params, img_bbox)
            
            # Compute constraint losses
            all_boxes = [title_box] + cap_boxes
            loss = (
                10 * ConstraintLoss.overlap_loss(all_boxes) +
                2 * ConstraintLoss.alignment_loss(all_boxes) +
                5 * ConstraintLoss.hierarchy_loss(title_box, cap_boxes) +
                3 * ConstraintLoss.border_loss(all_boxes, self.W, self.H) +
                1 * ConstraintLoss.balance_loss(all_boxes, self.W, self.H)
            )
            
            loss.backward()
            optimizer.step()
        
        # Final layout
        with torch.no_grad():
            final_params = self.gan(z)[0]
            title_box, cap_boxes = self._decode_layout(final_params, img_bbox)
        
        return self._create_layout_dict(title_box, cap_boxes, title, captions, img_bbox)
    
    def _decode_layout(self, params, img_bbox):
        """Decode GAN output to bounding boxes"""
        # Title: params[0:4] = [x, y, w, h]
        tx = params[0].item() * self.W
        ty = params[1].item() * self.H
        tw = params[2].item() * 300 + 100
        th = params[3].item() * 150 + 50
        title_box = [tx, ty, tx+tw, ty+th]
        
        # Captions: params[4:10] for 2 captions
        cap_boxes = []
        for i in range(2):
            cx = params[4+i*3].item() * self.W
            cy = params[5+i*3].item() * self.H
            cw = params[6+i*3].item() * 200 + 50
            ch = 40
            cap_boxes.append([cx, cy, cx+cw, cy+ch])
        
        return title_box, cap_boxes
    
    def _create_layout_dict(self, title_box, cap_boxes, title, captions, img_bbox):
        """Convert boxes to layout dictionary"""
        from src.color_contrast import get_average_color, adjust_text_color
        
        layouts = []
        
        # Title layout
        tx = (title_box[0] + title_box[2]) / 2
        ty = (title_box[1] + title_box[3]) / 2
        font_size = random.randint(100, 250)
        align = self._get_alignment(tx)
        
        layouts.append({
            'text': title, 'x': int(tx), 'y': int(ty),
            'size': font_size, 'font': random.choice(self.fonts),
            'color': (255, 255, 255), 'align': align,
            'bbox': [int(x) for x in title_box]
        })
        
        # Caption layouts
        num_caps = random.choice([0, 1, 2])
        for i in range(min(num_caps, len(captions))):
            cx = (cap_boxes[i][0] + cap_boxes[i][2]) / 2
            cy = (cap_boxes[i][1] + cap_boxes[i][3]) / 2
            cap_align = align if align == 'center' else random.choice(['left', 'center', 'right'])
            
            layouts.append({
                'text': captions[i], 'x': int(cx), 'y': int(cy),
                'size': max(20, font_size//2), 'font': layouts[0]['font'],
                'color': (255, 255, 255), 'align': cap_align,
                'bbox': [int(x) for x in cap_boxes[i]]
            })
        
        return layouts
    
    def _get_alignment(self, x):
        """Determine alignment from x position"""
        if x < self.W / 3:
            return 'left'
        elif x > 2 * self.W / 3:
            return 'right'
        return 'center'
