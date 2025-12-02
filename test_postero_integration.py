"""Test PosterO Integration with Key2Poster Pipeline

This script demonstrates how to use PosterO for layout generation
and integrate it with the Key2Poster pipeline.
"""

import sys
from pathlib import Path
from PIL import Image
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from layout_gan import PosterO
from postero_pipeline import PosterOPipeline

def test_basic_layout_generation():
    """Test basic layout generation with PosterO"""
    print("=" * 60)
    print("Test 1: Basic Layout Generation")
    print("=" * 60)
    
    # Initialize PosterO
    postero = PosterO(
        canvas_size=(720, 1080),
        device='cuda'
    )
    
    # Create dummy image
    dummy_image = Image.new('RGB', (720, 1080), color='white')
    
    # Generate layout
    keywords = ["summer", "sale", "event"]
    layout = postero.generate_layout(dummy_image, keywords)
    
    print(f"\nGenerated Layout:")
    print(f"  Layers: {len(layout['layers'])}")
    for i, layer in enumerate(layout['layers']):
        print(f"  Layer {i}: {layer['type']} - bbox: {layer['bbox']}")
    
    # Convert to template
    template = postero.layout_to_template(layout)
    print(f"\nTemplate Format:")
    print(f"  Size: {template['size']}")
    print(f"  Layers: {len(template['layers'])}")
    
    return template

def test_full_pipeline():
    """Test full PosterO pipeline"""
    print("\n" + "=" * 60)
    print("Test 2: Full PosterO Pipeline")
    print("=" * 60)
    
    # Initialize full pipeline
    pipeline = PosterOPipeline(
        canvas_size=(720, 1080),
        use_official=False  # Use fallback for testing
    )
    
    # Create dummy image
    dummy_image = Image.new('RGB', (720, 1080), color='lightblue')
    
    # Generate layout
    keywords = "cyberpunk neon city"
    layout = pipeline.generate_layout(dummy_image, keywords, num_elements=3)
    
    print(f"\nGenerated Layout:")
    for i, layer in enumerate(layout['layers']):
        print(f"  Layer {i}: {layer['type']} - bbox: {layer['bbox']}")
    
    # Convert to template
    template = pipeline.layout_to_template(layout)
    
    # Save template
    output_path = Path(__file__).parent / 'templates' / 'postero_generated.json'
    pipeline.save_template(template, output_path)
    
    return template

def test_with_key2poster_pipeline():
    """Test integration with Key2Poster pipeline"""
    print("\n" + "=" * 60)
    print("Test 3: Integration with Key2Poster")
    print("=" * 60)
    
    try:
        from pipeline import Key2PosterPipeline
        
        # Generate layout with PosterO
        postero = PosterO(canvas_size=(720, 1080))
        dummy_image = Image.new('RGB', (720, 1080), color='white')
        layout = postero.generate_layout(dummy_image, ["anime", "love", "story"])
        template = postero.layout_to_template(layout)
        
        # Save template
        template_path = Path(__file__).parent / 'templates' / 'postero_test.json'
        template_path.parent.mkdir(exist_ok=True)
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"\nTemplate saved to: {template_path}")
        print(f"You can now use this template with Key2Poster pipeline!")
        
        # Show how to use with pipeline
        print("\nUsage with Key2Poster:")
        print("  pipeline = Key2PosterPipeline(use_flux=True)")
        print(f"  image, brief, metrics = pipeline.generate_poster(")
        print(f"      'anime love story',")
        print(f"      template_path='{template_path}',")
        print(f"      output_path='poster.png'")
        print(f"  )")
        
        return template
        
    except ImportError as e:
        print(f"Could not import Key2PosterPipeline: {e}")
        print("Make sure pipeline.py is in the src/ directory")
        return None

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PosterO Integration Tests")
    print("=" * 60)
    
    # Test 1: Basic layout generation
    template1 = test_basic_layout_generation()
    
    # Test 2: Full pipeline
    template2 = test_full_pipeline()
    
    # Test 3: Integration with Key2Poster
    template3 = test_with_key2poster_pipeline()
    
    print("\n" + "=" * 60)
    print("All Tests Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. To use official PosterO with LLM:")
    print("   - Download LLaMA 3.1-8B model")
    print("   - Set llm_path in PosterO initialization")
    print("   - Set use_official=True in PosterOPipeline")
    print("\n2. To train design intent detector:")
    print("   - Follow PosterO-CVPR2025/design_intent_detect/README.md")
    print("   - Set intent_model_path in PosterO initialization")
    print("\n3. To generate posters with PosterO layouts:")
    print("   - Use generated templates with Key2Poster pipeline")
    print("   - Templates are saved in templates/ directory")

if __name__ == "__main__":
    main()
