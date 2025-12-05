#!/usr/bin/env python3
"""
Use pre-generated layouts from .tmp checkpoint file
Combines FLUX image generation with existing PosterO layouts
"""

import torch
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_tmp_layouts(tmp_path):
    """Load layouts from .tmp checkpoint file"""
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
    return valid_count >= 2  # At least 2 valid non-canvas elements

def get_random_layout(tmp_data, split='valid', max_tries=50):
    """Get a random valid layout from the checkpoint"""
    samples = tmp_data[split]
    
    for _ in range(max_tries):
        sample = random.choice(samples)
        layout = sample['generated']['layout'][0]
        
        if is_valid_layout(layout):
            return {
                'cls_elem': layout['cls_elem'],
                'box_elem': layout['box_elem'],
                'svg': sample['generated']['svg'][0]
            }
    
    # Fallback: return any layout
    sample = samples[0]
    layout = sample['generated']['layout'][0]
    return {
        'cls_elem': layout['cls_elem'],
        'box_elem': layout['box_elem'],
        'svg': sample['generated']['svg'][0]
    }

def apply_layout_to_image(image, layout, canvas_size=(513, 750)):
    """Apply PosterO layout to FLUX-generated image"""
    
    # Create canvas
    canvas = Image.new('RGB', canvas_size, (250, 239, 207))
    
    # Find image region (usually the largest non-canvas element)
    img_bbox = None
    max_area = 0
    
    for cls, bbox in zip(layout['cls_elem'], layout['box_elem']):
        if cls != 'canvas':
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            if area > max_area:
                max_area = area
                img_bbox = bbox
    
    # Resize and paste image
    if img_bbox:
        x1, y1, x2, y2 = img_bbox
        img_w, img_h = x2 - x1, y2 - y1
        
        # Validate dimensions
        if img_w > 0 and img_h > 0:
            image_resized = image.resize((img_w, img_h))
            canvas.paste(image_resized, (x1, y1))
            print(f"  ✓ Placed image at {img_bbox}")
        else:
            # Invalid bbox, use full canvas
            canvas.paste(image.resize(canvas_size), (0, 0))
            print(f"  ⚠ Invalid image bbox {img_bbox}, using full canvas")
    else:
        # Fallback: center the image
        canvas.paste(image.resize(canvas_size), (0, 0))
        print(f"  ✓ Placed image (full canvas)")
    
    # Add text overlays
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_large = ImageFont.truetype("fonts/Graduate-Regular.ttf", 36)
        font_small = ImageFont.truetype("fonts/Graduate-Regular.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    for cls, bbox in zip(layout['cls_elem'], layout['box_elem']):
        x1, y1, x2, y2 = bbox
        
        # Validate bbox
        if x2 <= x1 or y2 <= y1:
            print(f"  ⚠ Skipping invalid {cls} bbox: {bbox}")
            continue
        
        if 'text' in cls.lower():
            # Determine text based on element type
            if 'heading' in cls.lower() or cls == 'text':
                text = "POSTER TITLE"
                font = font_large
                color = (255, 255, 255)
            else:
                text = "Subtitle"
                font = font_small
                color = (200, 200, 200)
            
            # Center text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            text_x = max(0, x1 + (x2 - x1 - text_w) // 2)
            text_y = max(0, y1 + (y2 - y1 - text_h) // 2)
            
            # Shadow
            draw.text((text_x+2, text_y+2), text, font=font, fill=(0, 0, 0))
            draw.text((text_x, text_y), text, font=font, fill=color)
            
            print(f"  ✓ Added {cls} at {bbox}")
        
        elif 'underlay' in cls.lower():
            # Draw semi-transparent underlay
            overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0, 128))
            canvas.paste(Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB'))
            print(f"  ✓ Added {cls} at {bbox}")
    
    return canvas

def generate_poster_with_tmp(keywords, tmp_path, output_path="output_with_tmp.png", use_flux=True, test_image=None):
    """
    Generate poster using FLUX + pre-generated PosterO layout
    
    Args:
        keywords: Keywords for FLUX generation
        tmp_path: Path to .tmp checkpoint file
        output_path: Output path for final poster
        use_flux: If True, generate with FLUX. If False, use test_image
        test_image: Path to test image (used if use_flux=False)
    """
    
    print("="*60)
    print("FLUX + PosterO (from .tmp file)")
    print("="*60)
    
    # Load layouts from checkpoint
    print(f"\n[1/3] Loading layouts from {tmp_path}...")
    tmp_data = load_tmp_layouts(tmp_path)
    print(f"  ✓ Loaded {len(tmp_data['valid'])} valid samples")
    print(f"  ✓ Loaded {len(tmp_data['test'])} test samples")
    print(f"  ✓ Checkpoint: {tmp_data['checkpoint']}")
    
    # Get random layout
    layout = get_random_layout(tmp_data, split='valid')
    print(f"\n  Selected layout:")
    print(f"    Elements: {layout['cls_elem']}")
    print(f"    Bboxes: {len(layout['box_elem'])}")
    
    # Generate or load image
    if use_flux:
        print(f"\n[2/3] Generating image with FLUX...")
        try:
            from src.visual_generator_flux import VisualGeneratorFlux
            
            flux_gen = VisualGeneratorFlux()
            prompt = f"{keywords}, poster art, no text, clean image"
            
            # Generate at standard size first
            image = flux_gen.generate(prompt, width=512, height=768, seed=42)
            print(f"  ✓ Generated {image.size}")
        except Exception as e:
            print(f"  ✗ FLUX failed: {e}")
            print(f"  Using dummy image instead...")
            image = Image.new('RGB', (512, 768), (100, 150, 200))
    else:
        print(f"\n[2/3] Loading test image...")
        if test_image and Path(test_image).exists():
            image = Image.open(test_image)
            print(f"  ✓ Loaded {image.size}")
        else:
            print(f"  Creating dummy image...")
            image = Image.new('RGB', (512, 768), (100, 150, 200))
    
    # Apply layout
    print(f"\n[3/3] Applying PosterO layout...")
    canvas_size = (513, 750)  # Standard PosterO canvas size
    final_poster = apply_layout_to_image(image, layout, canvas_size)
    
    # Save
    final_poster.save(output_path)
    print(f"\n✅ Poster saved: {output_path}")
    print(f"  Size: {final_poster.size}")
    
    return final_poster, layout

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate poster using FLUX + PosterO .tmp layouts")
    parser.add_argument("--keywords", default="anime love story", help="Keywords for FLUX")
    parser.add_argument("--tmp", default="PosterO/TinyLlama-1.1B-Chat-v1.0/pku/hierarchical_top_EXP1_1.pt.tmp", 
                        help="Path to .tmp checkpoint file")
    parser.add_argument("--output", default="output_with_tmp.png", help="Output path")
    parser.add_argument("--no-flux", action="store_true", help="Don't use FLUX, use dummy/test image")
    parser.add_argument("--test-image", default=None, help="Test image path (if --no-flux)")
    
    args = parser.parse_args()
    
    generate_poster_with_tmp(args.keywords, args.tmp, args.output, 
                            use_flux=not args.no_flux, test_image=args.test_image)
