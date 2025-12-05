#!/usr/bin/env python3
"""
Test PosterO layout application only (no FLUX)
Uses dummy image to test layout system
"""

import torch
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def load_layouts(tmp_path):
    """Load pre-generated layouts"""
    data = torch.load(tmp_path, map_location='cpu', weights_only=False)
    return data

def is_valid_layout(layout):
    """Check if layout has valid bboxes"""
    valid_count = 0
    for cls, bbox in zip(layout['cls_elem'], layout['box_elem']):
        if cls == 'canvas':
            continue
        x1, y1, x2, y2 = bbox
        if x2 > x1 and y2 > y1:
            valid_count += 1
    return valid_count >= 2

def get_layout(tmp_data, split='valid', index=None, max_tries=50):
    """Get layout by index or random (with validation)"""
    samples = tmp_data[split]
    
    if index is not None:
        sample = samples[index]
        layout = sample['generated']['layout'][0]
        return {
            'cls_elem': layout['cls_elem'],
            'box_elem': layout['box_elem'],
            'original_data': sample
        }
    
    # Random with validation
    for _ in range(max_tries):
        sample = random.choice(samples)
        layout = sample['generated']['layout'][0]
        
        if is_valid_layout(layout):
            return {
                'cls_elem': layout['cls_elem'],
                'box_elem': layout['box_elem'],
                'original_data': sample
            }
    
    # Fallback
    sample = samples[0]
    layout = sample['generated']['layout'][0]
    return {
        'cls_elem': layout['cls_elem'],
        'box_elem': layout['box_elem'],
        'original_data': sample
    }

def visualize_layout(layout, output_path="test_layout.png"):
    """Visualize layout with colored boxes"""
    canvas_size = (513, 750)
    canvas = Image.new('RGB', canvas_size, (250, 239, 207))
    draw = ImageDraw.Draw(canvas)
    
    colors = {
        'canvas': (200, 200, 200),
        'text': (0, 255, 0),
        'logo': (255, 0, 0),
        'underlay': (255, 165, 0),
        'embellishment': (0, 0, 255)
    }
    
    print(f"\nLayout elements:")
    for i, (cls, bbox) in enumerate(zip(layout['cls_elem'], layout['box_elem'])):
        x1, y1, x2, y2 = bbox
        
        # Validate
        if x2 <= x1 or y2 <= y1:
            print(f"  {i}. {cls}: INVALID {bbox}")
            continue
        
        # Get color
        color = colors.get(cls, (128, 128, 128))
        
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Add label
        try:
            font = ImageFont.truetype("fonts/Graduate-Regular.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        label = f"{cls}_{i}"
        draw.text((x1+5, y1+5), label, fill=color, font=font)
        
        print(f"  {i}. {cls}: [{x1}, {y1}, {x2}, {y2}] size=({x2-x1}x{y2-y1})")
    
    canvas.save(output_path)
    print(f"\n✅ Saved: {output_path}")
    return canvas

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--tmp", default="PosterO/TinyLlama-1.1B-Chat-v1.0/pku/hierarchical_top_EXP1_1.pt.tmp")
    parser.add_argument("--output", default="test_layout.png")
    parser.add_argument("--index", type=int, default=None, help="Layout index (default: random)")
    parser.add_argument("--count", type=int, default=1, help="Number of layouts to test")
    
    args = parser.parse_args()
    
    print("="*60)
    print("PosterO Layout Test (No FLUX)")
    print("="*60)
    
    # Load layouts
    print(f"\nLoading: {args.tmp}")
    data = load_layouts(args.tmp)
    print(f"✓ Loaded {len(data['valid'])} valid, {len(data['test'])} test samples")
    
    # Test multiple layouts
    for i in range(args.count):
        print(f"\n--- Layout {i+1}/{args.count} ---")
        layout = get_layout(data, split='valid', index=args.index)
        
        output = args.output if args.count == 1 else f"test_layout_{i}.png"
        visualize_layout(layout, output)
