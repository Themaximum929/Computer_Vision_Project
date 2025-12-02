"""Test PosterO Full Pipeline Implementation

Demonstrates the complete PosterO pipeline:
1. Design Intent Detection
2. Saliency Detection
3. Layout Tree Generation
4. Template Conversion
"""

from src.postero_pipeline import PosterOPipeline
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image(size=(720, 1080)):
    """Create a test image for layout generation"""
    img = Image.new('RGB', size, color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add some visual elements
    draw.rectangle([100, 100, 620, 500], fill='#4a90e2', outline='#2c5aa0', width=3)
    draw.ellipse([200, 600, 520, 900], fill='#e74c3c', outline='#c0392b', width=3)
    
    return img

def visualize_layout(image, layout, output_path):
    """Visualize layout on image"""
    img = image.copy()
    draw = ImageDraw.Draw(img, 'RGBA')
    
    colors = {
        'background': (200, 200, 200, 50),
        'image': (74, 144, 226, 100),
        'text': (231, 76, 60, 100),
        'logo': (46, 204, 113, 100)
    }
    
    for layer in layout['layers']:
        if layer['type'] == 'background':
            continue
        
        bbox = layer['bbox']
        color = colors.get(layer['type'], (128, 128, 128, 100))
        
        # Draw rectangle
        draw.rectangle(bbox, fill=color, outline=color[:3] + (255,), width=3)
        
        # Add label
        label_pos = (bbox[0] + 10, bbox[1] + 10)
        draw.text(label_pos, layer['type'].upper(), fill='black')
    
    img.save(output_path)
    print(f"✓ Visualization saved to {output_path}")

def main():
    print("=" * 60)
    print("PosterO Full Pipeline Test")
    print("=" * 60)
    
    # Initialize PosterO pipeline
    print("\n[1] Initializing PosterO Pipeline...")
    pipeline = PosterOPipeline(
        canvas_size=(720, 1080),
        use_official=True  # Try official, fallback if unavailable
    )
    
    # Create test image
    print("\n[2] Creating test image...")
    test_image = create_test_image()
    test_image.save('outputs/postero_test_input.png')
    print("✓ Test image created")
    
    # Test cases
    test_cases = [
        {
            'name': 'Movie Poster',
            'keywords': 'cyberpunk neon city action',
            'num_elements': 3
        },
        {
            'name': 'Event Poster',
            'keywords': 'summer music festival concert',
            'num_elements': 4
        },
        {
            'name': 'Minimal Design',
            'keywords': 'minimalist modern clean',
            'num_elements': 2
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n[{i+3}] Generating layout: {test['name']}")
        print(f"    Keywords: {test['keywords']}")
        print(f"    Elements: {test['num_elements']}")
        
        # Generate layout
        layout = pipeline.generate_layout(
            test_image,
            test['keywords'],
            num_elements=test['num_elements']
        )
        
        print(f"    ✓ Layout generated with {len(layout['layers'])} layers")
        
        # Convert to template
        template = pipeline.layout_to_template(layout)
        
        # Save template
        template_path = f'outputs/postero_template_{i+1}.json'
        pipeline.save_template(template, template_path)
        
        # Visualize
        viz_path = f'outputs/postero_layout_{i+1}.png'
        visualize_layout(test_image, layout, viz_path)
        
        # Print layout details
        print(f"    Layout structure:")
        for layer in layout['layers']:
            bbox = layer['bbox']
            print(f"      - {layer['type']:12s}: [{bbox[0]:4d}, {bbox[1]:4d}, {bbox[2]:4d}, {bbox[3]:4d}]")
    
    print("\n" + "=" * 60)
    print("PosterO Pipeline Test Complete!")
    print("=" * 60)
    print("\nKey Differences from GAN approach:")
    print("  ✓ Content-aware layout (design intent + saliency)")
    print("  ✓ Hierarchical layout trees (not flat bounding boxes)")
    print("  ✓ LLM-based generation (not random noise)")
    print("  ✓ In-context learning (not adversarial training)")
    print("\nFiles generated:")
    print("  - outputs/postero_test_input.png")
    print("  - outputs/postero_template_*.json")
    print("  - outputs/postero_layout_*.png")

if __name__ == '__main__':
    main()
