"""Latent Optimization - Constraint-based refinement"""
import torch
import numpy as np

class LatentOptimizer:
    """Optimize layout in latent space with constraints"""
    
    def __init__(self, layout_gan):
        self.layout_gan = layout_gan
        self.device = layout_gan.device
    
    def optimize(self, img_features, text_features, iterations=50, lr=0.01):
        """Optimize latent vector z to satisfy constraints"""
        # Set generator to eval mode (fixes BatchNorm with batch_size=1)
        self.layout_gan.generator.eval()
        
        # Initialize random z
        z = torch.randn(1, 128, requires_grad=True, device=self.device)
        
        if not isinstance(img_features, torch.Tensor):
            img_features = torch.tensor(img_features, dtype=torch.float32).unsqueeze(0).to(self.device)
        if not isinstance(text_features, torch.Tensor):
            text_features = torch.tensor(text_features, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        optimizer = torch.optim.Adam([z], lr=lr)
        
        best_z = z.clone()
        best_loss = float('inf')
        
        for i in range(iterations):
            optimizer.zero_grad()
            
            # Generate layout
            layout = self.layout_gan.generator(z, img_features, text_features)
            
            # Compute constraint losses
            loss = self.compute_loss(layout)
            
            if loss.item() < best_loss:
                best_loss = loss.item()
                best_z = z.clone()
            
            loss.backward()
            optimizer.step()
            
            if i % 10 == 0:
                print(f"  Optimization iter {i}/{iterations}: loss={loss.item():.4f}")
        
        # Generate final layout with best z
        with torch.no_grad():
            final_layout = self.layout_gan.generator(best_z, img_features, text_features)
        
        return final_layout.cpu().numpy()[0], best_loss
    
    def compute_loss(self, layout):
        """Compute total constraint loss"""
        # layout shape: [batch, num_elements, 7]
        
        overlap_loss = self.overlap_constraint(layout)
        alignment_loss = self.alignment_constraint(layout)
        hierarchy_loss = self.hierarchy_constraint(layout)
        border_loss = self.border_constraint(layout)
        balance_loss = self.balance_constraint(layout)
        
        # Weighted sum (10x overlap penalty to prevent collisions)
        total_loss = (
            10.0 * overlap_loss +
            0.5 * alignment_loss +
            0.3 * hierarchy_loss +
            0.8 * border_loss +
            0.4 * balance_loss
        )
        
        return total_loss
    
    def overlap_constraint(self, layout):
        """Penalize overlapping elements"""
        # layout: [batch, num_elements, 7] -> [x1, y1, x2, y2, type_logits]
        bboxes = layout[:, :, :4]  # [batch, num_elements, 4]
        
        loss = 0.0
        num_elements = bboxes.size(1)
        
        for i in range(num_elements):
            for j in range(i + 1, num_elements):
                iou = self.compute_iou(bboxes[:, i], bboxes[:, j])
                loss += torch.relu(iou)  # Penalize any overlap
        
        return loss
    
    def compute_iou(self, box1, box2):
        """Compute IoU between two boxes"""
        # box: [batch, 4] -> [x1, y1, x2, y2]
        x1_max = torch.max(box1[:, 0], box2[:, 0])
        y1_max = torch.max(box1[:, 1], box2[:, 1])
        x2_min = torch.min(box1[:, 2], box2[:, 2])
        y2_min = torch.min(box1[:, 3], box2[:, 3])
        
        inter_w = torch.relu(x2_min - x1_max)
        inter_h = torch.relu(y2_min - y1_max)
        inter_area = inter_w * inter_h
        
        area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
        area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])
        union_area = area1 + area2 - inter_area
        
        iou = inter_area / (union_area + 1e-6)
        return iou.mean()
    
    def alignment_constraint(self, layout):
        """Encourage alignment to grid"""
        bboxes = layout[:, :, :4]
        
        # Grid lines (thirds)
        grid_lines = torch.tensor([1/3, 2/3, 0.5], device=self.device)
        
        loss = 0.0
        for i in range(bboxes.size(1)):
            center_x = (bboxes[:, i, 0] + bboxes[:, i, 2]) / 2
            center_y = (bboxes[:, i, 1] + bboxes[:, i, 3]) / 2
            
            # Distance to nearest grid line
            dist_x = torch.min(torch.abs(center_x.unsqueeze(-1) - grid_lines), dim=-1)[0]
            dist_y = torch.min(torch.abs(center_y.unsqueeze(-1) - grid_lines), dim=-1)[0]
            
            loss += dist_x.mean() + dist_y.mean()
        
        return loss
    
    def hierarchy_constraint(self, layout):
        """Enforce size hierarchy (title > caption)"""
        bboxes = layout[:, :, :4]
        types = layout[:, :, 4:]  # [batch, num_elements, 3]
        
        loss = 0.0
        
        # Compute areas
        areas = (bboxes[:, :, 2] - bboxes[:, :, 0]) * (bboxes[:, :, 3] - bboxes[:, :, 1])
        
        # Title should be larger than captions
        # Assuming: type[0]=image, type[1]=title, type[2]=caption
        for i in range(areas.size(1)):
            for j in range(i + 1, areas.size(1)):
                # If i is title and j is caption, enforce area_i > area_j
                is_title_i = types[:, i, 1]
                is_caption_j = types[:, j, 2]
                
                violation = torch.relu(areas[:, j] - areas[:, i]) * is_title_i * is_caption_j
                loss += violation.mean()
        
        return loss
    
    def border_constraint(self, layout):
        """Ensure minimum margin from edges"""
        bboxes = layout[:, :, :4]
        margin = 0.05  # 5% margin
        
        loss = 0.0
        
        # Check all edges
        loss += torch.relu(margin - bboxes[:, :, 0]).mean()  # Left
        loss += torch.relu(margin - bboxes[:, :, 1]).mean()  # Top
        loss += torch.relu(bboxes[:, :, 2] - (1 - margin)).mean()  # Right
        loss += torch.relu(bboxes[:, :, 3] - (1 - margin)).mean()  # Bottom
        
        return loss
    
    def balance_constraint(self, layout):
        """Encourage balanced composition"""
        bboxes = layout[:, :, :4]
        
        # Compute center of mass
        areas = (bboxes[:, :, 2] - bboxes[:, :, 0]) * (bboxes[:, :, 3] - bboxes[:, :, 1])
        centers_x = (bboxes[:, :, 0] + bboxes[:, :, 2]) / 2
        centers_y = (bboxes[:, :, 1] + bboxes[:, :, 3]) / 2
        
        total_area = areas.sum(dim=1, keepdim=True)
        com_x = (areas * centers_x).sum(dim=1) / total_area.squeeze()
        com_y = (areas * centers_y).sum(dim=1) / total_area.squeeze()
        
        # Distance from canvas center (0.5, 0.5)
        loss = (com_x - 0.5).pow(2) + (com_y - 0.5).pow(2)
        
        return loss.mean()
