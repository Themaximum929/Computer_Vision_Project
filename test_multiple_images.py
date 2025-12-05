#!/usr/bin/env python3
"""
Test combine_simple with multiple FLUX-generated images + add text
"""

import os
import sys
import subprocess
sys.path.insert(0, 'src')
from visual_generator_flux import VisualGeneratorFlux
from add_text_to_poster import add_text_to_poster

# Test prompts with titles and captions
TEST_CASES = [
    {
        "prompt": "vintage travel poster, retro style, mountains and lake, warm colors",
        "title": "ALPINE ADVENTURE",
        "captions": ["Discover Switzerland", "Summer 2024"]
    },
    {
        "prompt": "sci-fi movie poster, futuristic city, neon lights, cyberpunk",
        "title": "NEON CITY",
        "captions": ["Coming Soon", "In Theaters 2024"]
    },
    {
        "prompt": "food menu poster, restaurant, elegant typography, minimalist",
        "title": "BISTRO MENU",
        "captions": ["Fresh Daily", "Reserve Now"]
    },
    {
        "prompt": "sports event poster, dynamic action, bold colors, athletic",
        "title": "CHAMPIONSHIP",
        "captions": ["Finals 2024", "Get Tickets"]
    },
    {
        "prompt": "art exhibition poster, abstract shapes, modern art, gallery",
        "title": "MODERN ART",
        "captions": ["Gallery Opening", "March 15-30"]
    }
]


def generate_flux_images(num_images=3):
    """Generate test images using FLUX."""
    print("=== Generating Test Images with FLUX ===")
    
    # Load FLUX model with memory-efficient settings
    print("Loading FLUX model...")
    generator = VisualGeneratorFlux(model_id="black-forest-labs/FLUX.1-schnell")
    
    image_paths = []
    
    for i, test_case in enumerate(TEST_CASES[:num_images]):
        prompt = test_case["prompt"]
        print(f"\n[{i+1}/{num_images}] Generating: {prompt}")
        
        # Generate image at model's native size to avoid distortion
        image = generator.generate(
            prompt=prompt,
            width=512,  # Close to 513
            height=768,  # Close to 750
            num_inference_steps=4,
            seed=42 + i
        )
        
        # Resize to exact model size
        from PIL import Image as PILImage
        image = image.resize((513, 750), PILImage.LANCZOS)
        
        # Save image
        output_path = f"test_image_{i+1}.png"
        image.save(output_path)
        image_paths.append(output_path)
        print(f"✓ Saved to {output_path}")
    
    return image_paths


def run_combine_simple(image_path, output_prefix):
    """Run combine_simple.py on an image."""
    print(f"\n=== Processing {image_path} ===")
    
    # Run combine_simple.py
    result = subprocess.run(
        ["python", "combine_simple.py", image_path],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    # Rename outputs
    if os.path.exists("combined_output.svg"):
        os.rename("combined_output.svg", f"{output_prefix}_output.svg")
    if os.path.exists("combined_visualization.png"):
        os.rename("combined_visualization.png", f"{output_prefix}_visualization.png")
    
    return True


def main():
    num_images = 3
    if len(sys.argv) > 1:
        num_images = int(sys.argv[1])
    
    print(f"Testing with {num_images} FLUX-generated images\n")
    
    # Generate test images
    image_paths = generate_flux_images(num_images)
    
    # Process each image
    print("\n" + "="*60)
    print("Processing Images with Part 1 + Part 2 Pipeline")
    print("="*60)
    
    for i, image_path in enumerate(image_paths):
        output_prefix = f"result_{i+1}"
        test_case = TEST_CASES[i]
        
        # Step 1: Generate layout
        success = run_combine_simple(image_path, output_prefix)
        
        if success:
            print(f"✓ Layout generated:")
            print(f"  - {output_prefix}_output.svg")
            print(f"  - {output_prefix}_visualization.png")
            
            # Step 2: Add text to poster
            print(f"\n[Adding Text] Title: '{test_case['title']}'")
            svg_path = f"{output_prefix}_output.svg"
            final_output = f"{output_prefix}_final.png"
            
            add_text_to_poster(
                image_path=image_path,
                svg_path=svg_path,
                title=test_case['title'],
                captions=test_case['captions'],
                output_path=final_output,
                style_prompt=test_case['prompt']
            )
            print(f"✓ Final poster: {final_output}")
    
    print("\n" + "="*60)
    print("Complete! Check these files:")
    print("  - result_*_visualization.png (layout visualization)")
    print("  - result_*_final.png (poster with text)")
    print("="*60)


if __name__ == "__main__":
    main()
