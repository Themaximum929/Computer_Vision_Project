#!/usr/bin/env python3
"""
Integration test: FLUX image generation + PosterO layout generation
Combines upper part (your work) with lower part (classmate's work)
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "src" / "generalized_setting"))

def test_integration(keywords="anime love story", output_path="test_integration_output.png"):
    """
    Test the full integration:
    1. Generate image with FLUX (upper part - your work)
    2. Generate layout with PosterO (lower part - classmate's work)
    3. Compose final poster
    """
    
    print("="*60)
    print("INTEGRATION TEST: FLUX + PosterO")
    print("="*60)
    
    # ===== UPPER PART: FLUX Image Generation (Your Work) =====
    print("\n[UPPER PART] Generating image with FLUX...")
    from src.visual_generator_flux import VisualGeneratorFlux
    
    flux_gen = VisualGeneratorFlux()
    prompt = f"{keywords}, poster art, no text"
    image = flux_gen.generate(prompt, width=512, height=768, seed=42)
    
    # Save intermediate image
    temp_image_path = "temp_flux_image.png"
    image.save(temp_image_path)
    print(f"✓ FLUX image saved: {temp_image_path}")
    print(f"  Size: {image.size}")
    
    # ===== LOWER PART: PosterO Layout Generation (Classmate's Work) =====
    print("\n[LOWER PART] Generating layout with PosterO...")
    
    try:
        from pipeline import LayoutGenerationPipeline
        
        # Setup dataset info for movie-poster category
        dataset_info = {
            'dataset_name': 'pstylish7_movie-poster',
            'design_intent_bbox_dir': './PStylish7/movie-poster/predm_zs',
            'annotation_dir': './PStylish7/movie-poster',
            'label_info': {
                'T-G': {'type': 'text-general', 'color': 'green'},
                'T-H': {'type': 'text-heading', 'color': 'blue'},
                'L': {'type': 'logo', 'color': 'red'},
                'U': {'type': 'underlay', 'color': 'orange'},
                'E': {'type': 'embellishment', 'color': 'purple'}
            }
        }
        
        # Create pipeline
        pipeline = LayoutGenerationPipeline(
            dataset_info=dataset_info,
            strategy={'structure': 'plain', 'injection': 'top'},
            canvas_size=(512, 768),
            sample_size=5,
            rank_strategy='random'
        )
        
        # Create example design intent bboxes
        # These would normally come from a design intent detection model
        design_intent_bboxes = [
            (50, 50, 462, 200),   # Top region for title
            (50, 600, 462, 720)   # Bottom region for text
        ]
        
        # Generate layout
        result = pipeline.generate_layout(
            image=temp_image_path,
            design_intent_bboxes=design_intent_bboxes,
            num_generations=1
        )
        
        layout = result['layout_graphs'][0]
        svg_string = result['svg_results'][0]
        
        print(f"✓ Layout generated")
        print(f"  Elements: {layout['cls_elem']}")
        print(f"  Bboxes: {len(layout['box_elem'])}")
        
    except Exception as e:
        print(f"⚠ PosterO not available: {e}")
        print("  Using fallback template layout")
        
        # Fallback: simple template layout
        layout = {
            'cls_elem': ['canvas', 'text-heading', 'text-general'],
            'box_elem': [
                [0, 0, 512, 768],
                [50, 50, 462, 150],
                [50, 650, 462, 720]
            ]
        }
        svg_string = None
    
    # ===== COMPOSITION: Merge Image + Layout =====
    print("\n[COMPOSITION] Creating final poster...")
    
    # Create canvas
    canvas = Image.new('RGB', (512, 768), (250, 239, 207))
    
    # Paste FLUX image (assuming it fills most of the canvas)
    canvas.paste(image, (0, 0))
    
    # Add text overlays based on layout
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_large = ImageFont.truetype("fonts/Graduate-Regular.ttf", 40)
        font_small = ImageFont.truetype("fonts/Graduate-Regular.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add text based on layout elements
    for i, (cls, bbox) in enumerate(zip(layout['cls_elem'], layout['box_elem'])):
        if 'text' in cls.lower():
            x1, y1, x2, y2 = bbox
            
            if 'heading' in cls.lower():
                text = keywords.upper()
                font = font_large
                color = (255, 255, 255)
            else:
                text = "COMING SOON"
                font = font_small
                color = (200, 200, 200)
            
            # Center text in bbox
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            text_x = x1 + (x2 - x1 - text_w) // 2
            text_y = y1 + (y2 - y1 - text_h) // 2
            
            # Add shadow
            draw.text((text_x+2, text_y+2), text, font=font, fill=(0, 0, 0))
            draw.text((text_x, text_y), text, font=font, fill=color)
            
            print(f"  ✓ Added {cls}: '{text}' at ({x1},{y1},{x2},{y2})")
    
    # Save final poster
    canvas.save(output_path)
    print(f"\n✅ Final poster saved: {output_path}")
    print(f"  Size: {canvas.size}")
    
    # Cleanup
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    
    return canvas, layout


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FLUX + PosterO integration")
    parser.add_argument("--keywords", default="anime love story", help="Keywords for poster")
    parser.add_argument("--output", default="test_integration_output.png", help="Output path")
    
    args = parser.parse_args()
    
    test_integration(args.keywords, args.output)
