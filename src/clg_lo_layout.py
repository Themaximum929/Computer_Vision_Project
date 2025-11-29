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
    
    def generate_layout(self, img_bbox, title, captions, seed=None, poster_img=None):
        """Generate layout with constraint optimization"""
        if seed:
            torch.manual_seed(seed)
            np.random.seed(seed)
        
        self.poster_img = poster_img  # Store for color detection
        
        # Initial latent code
        z = torch.randn(1, 128, requires_grad=True)
        optimizer = torch.optim.Adam([z], lr=0.1)
        
        # Latent optimization loop
        for _ in range(50):
            optimizer.zero_grad()
            layout_params = self.gan(z)[0]
            
            # Decode to boxes
            title_box, cap_boxes, align_choice = self._decode_layout(layout_params, img_bbox)
            
            # Compute constraint losses
            all_boxes = [title_box] + cap_boxes
            loss = torch.tensor(
                10 * ConstraintLoss.overlap_loss(all_boxes) +
                2 * ConstraintLoss.alignment_loss(all_boxes) +
                5 * ConstraintLoss.hierarchy_loss(title_box, cap_boxes) +
                3 * ConstraintLoss.border_loss(all_boxes, self.W, self.H) +
                1 * ConstraintLoss.balance_loss(all_boxes, self.W, self.H),
                requires_grad=True
            )
            
            loss.backward()
            optimizer.step()
        
        # Final layout
        with torch.no_grad():
            final_params = self.gan(z)[0]
            title_box, cap_boxes, align_choice = self._decode_layout(final_params, img_bbox)
        
        return self._create_layout_dict(title_box, cap_boxes, title, captions, img_bbox, poster_img, align_choice)
    
    def _decode_layout(self, params, img_bbox):
        """Decode GAN output - randomly select alignment first, then position"""
        # Randomly select alignment (left/center/right) - force more variation
        align_choice = int(params[0].item() * 2.99)  # 0=left, 1=center, 2=right (avoid always getting 1)
        
        # Title position based on alignment
        ty = params[1].item() * (self.H - 350) + 50
        tw = params[2].item() * 200 + 200  # 200-400px width
        th = params[3].item() * 100 + 200  # 200-300px height
        
        if align_choice == 0:  # Left
            tx = 50  # 50px from left
        elif align_choice == 2:  # Right
            tx = self.W - tw - 50  # 50px from right
        else:  # Center
            tx = (self.W - tw) / 2
        
        title_box = [tx, ty, tx+tw, ty+th]
        
        # Captions: below title with same alignment rules
        cap_boxes = []
        for i in range(2):
            cy = params[4+i*2].item() * (self.H - title_box[3] - 150) + title_box[3] + 100  # Below title
            cw = params[5+i*2].item() * 150 + 150  # 150-300px width
            ch = 80
            
            # Caption alignment can differ from title (unless title is center)
            if align_choice == 1:  # Title is center, captions must be center
                cx = (self.W - cw) / 2
            else:  # Random caption alignment
                cap_align = int(params[6+i*2].item() * 3) if i < 1 else int(params[7+i*2].item() * 3)
                if cap_align == 0:  # Left - same left as title
                    cx = title_box[0]
                elif cap_align == 2:  # Right - same right as title
                    cx = title_box[2] - cw
                else:  # Center
                    cx = (self.W - cw) / 2
            
            cap_boxes.append([cx, cy, cx+cw, cy+ch])
        
        return title_box, cap_boxes, align_choice
    
    def _create_layout_dict(self, title_box, cap_boxes, title, captions, img_bbox, poster_img, align_choice):
        """Convert boxes to layout dictionary with proper font sizing and alignment"""
        from src.text_layout import resolve_text_positions
        from src.color_contrast import get_average_color, adjust_text_color
        from PIL import ImageDraw, ImageFont, Image
        
        # Use actual poster image for color detection
        if poster_img is None:
            poster_img = Image.new('RGB', (self.W, self.H), (250, 239, 207))
        draw = ImageDraw.Draw(poster_img)
        font_family = random.choice(self.fonts)
        
        # Use pre-determined alignment
        title_align = ['left', 'center', 'right'][align_choice]
        
        # Calculate font size to fit text in box
        def fit_font_size(text, bbox, min_size=20, max_size=250):
            box_w = bbox[2] - bbox[0]
            box_h = bbox[3] - bbox[1]
            
            for size in range(max_size, min_size - 1, -5):
                try:
                    font = ImageFont.truetype(f"fonts/{font_family}", size)
                except:
                    font = ImageFont.load_default()
                    return min_size, font
                
                # Wrap text
                words = text.split()
                lines = []
                current = []
                for word in words:
                    test = ' '.join(current + [word])
                    tb = draw.textbbox((0, 0), test, font=font)
                    if tb[2] - tb[0] <= box_w - 20:
                        current.append(word)
                    else:
                        if current:
                            lines.append(' '.join(current))
                        current = [word]
                if current:
                    lines.append(' '.join(current))
                
                # Check height
                total_h = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] + 5 for l in lines)
                if total_h <= box_h - 20:
                    return size, font
            
            return min_size, ImageFont.truetype(f"fonts/{font_family}", min_size)
        
        # Title with color contrast
        title_size, _ = fit_font_size(title, title_box, 100, 250)
        title_bg_color = get_average_color(poster_img, [int(x) for x in title_box])
        title_color = adjust_text_color(title_bg_color, (255, 255, 255))
        
        text_elements = [{'bbox': [int(x) for x in title_box], 'name': 'Title', 'priority': 1}]
        text_data = [{'text': title, 'size': title_size, 'font': font_family, 'align': title_align, 'color': title_color}]
        
        # Captions with alignment rules (at least 1 caption)
        num_caps = random.choice([1, 2])
        for i in range(min(num_caps, len(captions))):
            cap_center_x = (cap_boxes[i][0] + cap_boxes[i][2]) / 2
            if title_align == 'center':
                cap_align = 'center'
            else:
                cap_align = self._get_alignment(cap_center_x)
            
            cap_size, _ = fit_font_size(captions[i], cap_boxes[i], 20, max(20, title_size // 2))
            cap_bg_color = get_average_color(poster_img, [int(x) for x in cap_boxes[i]])
            cap_color = adjust_text_color(cap_bg_color, (255, 255, 255))
            
            text_elements.append({'bbox': [int(x) for x in cap_boxes[i]], 'name': f'Caption{i+1}', 'priority': 0})
            text_data.append({'text': captions[i], 'size': cap_size, 'font': font_family, 'align': cap_align, 'color': cap_color})
        
        # Resolve collisions
        adjusted = resolve_text_positions(text_elements, (self.W, self.H), img_bbox)
        
        # Build layouts with proper colors
        layouts = []
        for i, elem in enumerate(adjusted):
            layouts.append({
                'text': text_data[i]['text'],
                'size': text_data[i]['size'],
                'font': text_data[i]['font'],
                'color': text_data[i]['color'],
                'align': text_data[i]['align'],
                'bbox': elem['bbox']
            })
        
        return layouts
    
    def _get_alignment(self, x):
        """Determine alignment from x position (divide poster into 3 sections)"""
        if x < self.W / 3:
            return 'left'
        elif x > 2 * self.W / 3:
            return 'right'
        return 'center'
    
    def _get_caption_alignment(self, title_align):
        """Get caption alignment based on title alignment"""
        if title_align == 'center':
            return 'center'  # If title is center, all captions must be center
        else:
            return random.choice(['left', 'center', 'right'])  # Otherwise random
