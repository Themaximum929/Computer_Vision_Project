"""
Comparative Evaluation Module for 3 Poster Generation Methods
Measures: Layout Quality, Aesthetics, Readability, Performance
"""

import time
import numpy as np
from PIL import Image, ImageStat
import torch
from typing import Dict, List, Tuple
import json


class ComparativeEvaluator:
    """Evaluate and compare Template, LayoutGAN, and PosterO methods"""
    
    def __init__(self):
        self.results = {"template": [], "layoutgan": [], "postero": []}
    
    def evaluate_poster(self, image_path: str, layout_data: dict, method: str) -> Dict:
        """
        Evaluate a single poster across all metrics
        
        Args:
            image_path: Path to generated poster
            layout_data: Dict with 'title_bbox', 'caption_bboxes', 'image_bbox'
            method: 'template', 'layoutgan', or 'postero'
        
        Returns:
            Dict of all metrics
        """
        img = Image.open(image_path).convert('RGB')
        
        metrics = {
            # Layout metrics
            "alignment_score": self._compute_alignment(layout_data),
            "overlap_ratio": self._compute_overlap(layout_data, img.size),
            "balance_score": self._compute_balance(layout_data, img.size),
            
            # Aesthetic metrics
            "color_harmony": self._compute_color_harmony(img),
            "contrast_score": self._compute_contrast(img, layout_data),
            
            # Readability metrics
            "text_readability": self._compute_readability(img, layout_data),
            "text_coverage": self._compute_text_coverage(layout_data, img.size),
        }
        
        self.results[method].append(metrics)
        return metrics
    
    def _compute_alignment(self, layout: dict) -> float:
        """Measure how well elements align (0-1, higher is better)"""
        bboxes = []
        if 'title_bbox' in layout:
            bboxes.append(self._normalize_bbox(layout['title_bbox']))
        if 'caption_bboxes' in layout:
            bboxes.extend([self._normalize_bbox(b) for b in layout['caption_bboxes']])
        
        if len(bboxes) < 2:
            return 1.0
        
        # Check left/right/center alignment
        lefts = [b[0] for b in bboxes]
        rights = [b[2] for b in bboxes]
        centers = [(b[0] + b[2])/2 for b in bboxes]
        
        left_var = np.var(lefts) if len(lefts) > 1 else 0
        right_var = np.var(rights) if len(rights) > 1 else 0
        center_var = np.var(centers) if len(centers) > 1 else 0
        
        min_var = min(left_var, right_var, center_var)
        alignment = 1.0 / (1.0 + min_var / 1000)  # Normalize
        return float(alignment)
    
    def _compute_overlap(self, layout: dict, img_size: Tuple) -> float:
        """Measure text-image overlap (0-1, lower is better)"""
        if 'image_bbox' not in layout:
            return 0.0
        
        img_bbox = self._normalize_bbox(layout['image_bbox'])
        text_bboxes = []
        if 'title_bbox' in layout:
            text_bboxes.append(self._normalize_bbox(layout['title_bbox']))
        if 'caption_bboxes' in layout:
            text_bboxes.extend([self._normalize_bbox(b) for b in layout['caption_bboxes']])
        
        total_overlap = 0
        for tb in text_bboxes:
            overlap = self._bbox_intersection(img_bbox, tb)
            total_overlap += overlap
        
        img_area = (img_bbox[2] - img_bbox[0]) * (img_bbox[3] - img_bbox[1])
        return float(total_overlap / max(img_area, 1))
    
    def _normalize_bbox(self, bbox) -> Tuple:
        """Normalize bbox to (x1, y1, x2, y2) format"""
        if len(bbox) == 4:
            # Check if it's (x, y, w, h) or (x1, y1, x2, y2)
            if bbox[2] < bbox[0] or bbox[3] < bbox[1]:
                # It's (x, y, w, h)
                return (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
            # Already (x1, y1, x2, y2)
            return tuple(bbox)
        return tuple(bbox)
    
    def _bbox_intersection(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """Calculate intersection area of two bboxes (x1, y1, x2, y2)"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        if x2 < x1 or y2 < y1:
            return 0.0
        return (x2 - x1) * (y2 - y1)
    
    def _compute_balance(self, layout: dict, img_size: Tuple) -> float:
        """Measure visual balance (0-1, higher is better)"""
        w, h = img_size
        center_x, center_y = w / 2, h / 2
        
        # Calculate weighted center of all elements
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        all_bboxes = []
        if 'image_bbox' in layout:
            all_bboxes.append(self._normalize_bbox(layout['image_bbox']))
        if 'title_bbox' in layout:
            all_bboxes.append(self._normalize_bbox(layout['title_bbox']))
        if 'caption_bboxes' in layout:
            all_bboxes.extend([self._normalize_bbox(b) for b in layout['caption_bboxes']])
        
        for bbox in all_bboxes:
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            weighted_x += cx * area
            weighted_y += cy * area
            total_weight += area
        
        if total_weight == 0:
            return 0.5
        
        weighted_x /= total_weight
        weighted_y /= total_weight
        
        # Distance from center (normalized)
        dist = np.sqrt((weighted_x - center_x)**2 + (weighted_y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        balance = 1.0 - (dist / max_dist)
        return float(balance)
    
    def _compute_color_harmony(self, img: Image.Image) -> float:
        """Measure color harmony (0-1, higher is better)"""
        img_small = img.resize((100, 100))
        pixels = np.array(img_small).reshape(-1, 3)
        
        # Calculate color variance (lower = more harmonious)
        color_std = np.std(pixels, axis=0).mean()
        harmony = 1.0 / (1.0 + color_std / 50)
        return float(harmony)
    
    def _compute_contrast(self, img: Image.Image, layout: dict) -> float:
        """Measure text-background contrast (0-1, higher is better)"""
        text_bboxes = []
        if 'title_bbox' in layout:
            text_bboxes.append(self._normalize_bbox(layout['title_bbox']))
        if 'caption_bboxes' in layout:
            text_bboxes.extend([self._normalize_bbox(b) for b in layout['caption_bboxes']])
        
        if not text_bboxes:
            return 0.5
        
        contrasts = []
        for bbox in text_bboxes:
            x, y, x2, y2 = bbox
            w, h = x2 - x, y2 - y
            region = img.crop((x, y, x + w, y + h))
            stat = ImageStat.Stat(region)
            brightness = sum(stat.mean) / 3
            # Assume text is opposite brightness
            contrast = abs(brightness - 128) / 128
            contrasts.append(contrast)
        
        return float(np.mean(contrasts))
    
    def _compute_readability(self, img: Image.Image, layout: dict) -> float:
        """Measure text readability (0-1, higher is better)"""
        # Combines contrast and text size
        contrast = self._compute_contrast(img, layout)
        
        text_bboxes = []
        if 'title_bbox' in layout:
            text_bboxes.append(self._normalize_bbox(layout['title_bbox']))
        if 'caption_bboxes' in layout:
            text_bboxes.extend([self._normalize_bbox(b) for b in layout['caption_bboxes']])
        
        if not text_bboxes:
            return 0.5
        
        # Check if text is large enough
        avg_height = np.mean([b[3] - b[1] for b in text_bboxes])
        size_score = min(avg_height / 100, 1.0)  # 100px is ideal
        
        readability = (contrast + size_score) / 2
        return float(readability)
    
    def _compute_text_coverage(self, layout: dict, img_size: Tuple) -> float:
        """Measure text area coverage (0-1, 0.1-0.3 is ideal)"""
        w, h = img_size
        total_area = w * h
        
        text_area = 0
        if 'title_bbox' in layout:
            bbox = self._normalize_bbox(layout['title_bbox'])
            text_area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if 'caption_bboxes' in layout:
            for bbox in layout['caption_bboxes']:
                bbox = self._normalize_bbox(bbox)
                text_area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        
        coverage = text_area / total_area
        # Penalize too much or too little text
        ideal = 0.2
        score = 1.0 - abs(coverage - ideal) / ideal
        return float(max(0, score))
    
    def compare_methods(self) -> Dict:
        """Compare all 3 methods and return statistics"""
        comparison = {}
        
        for method in ['template', 'layoutgan', 'postero']:
            if not self.results[method]:
                continue
            
            metrics = {}
            for key in self.results[method][0].keys():
                values = [r[key] for r in self.results[method]]
                metrics[key] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
            
            comparison[method] = metrics
        
        return comparison
    
    def save_results(self, output_path: str):
        """Save evaluation results to JSON"""
        comparison = self.compare_methods()
        with open(output_path, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"Results saved to {output_path}")


def benchmark_generation_time(pipeline, keywords: str, num_runs: int = 3) -> Dict:
    """Benchmark generation time and memory"""
    times = []
    
    for i in range(num_runs):
        torch.cuda.empty_cache()
        start_mem = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        start_time = time.time()
        pipeline.generate_poster(keywords, output_path=f"temp_{i}.png", seed=42+i)
        end_time = time.time()
        
        end_mem = torch.cuda.max_memory_allocated() if torch.cuda.is_available() else 0
        
        times.append(end_time - start_time)
    
    return {
        'mean_time': float(np.mean(times)),
        'std_time': float(np.std(times)),
        'peak_memory_mb': float((end_mem - start_mem) / 1024 / 1024)
    }
