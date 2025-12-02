"""Demo: PosterO with LLM Integration

This script shows how to use PosterO with LLM for layout generation.
Run without LLM first, then with LLM after downloading the model.
"""

import sys
from pathlib import Path
from PIL import Image
import json

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_without_llm():
    """Demo using rule-based layout (no LLM required)"""
    print("\n" + "="*60)
    print("DEMO 1: PosterO WITHOUT LLM (Rule-based)")
    print("="*60)
    
    from postero_pipeline import PosterOPipeline
    
    pipeline = PosterOPipeline(
        canvas_size=(720, 1080),
        use_official=False  # Rule-based fallback
    )
    
    # Test cases
    test_cases = [
        ("summer sale event", 3),
        ("cyberpunk neon city", 3),
        ("anime love story", 3)
    ]
    
    for keywords, num_elements in test_cases:
        print(f"\nKeywords: '{keywords}'")
        
        dummy_img = Image.new('RGB', (720, 1080), 'white')
        layout = pipeline.generate_layout(dummy_img, keywords, num_elements)
        
        print(f"  Generated {len(layout['layers'])} layers:")
        for layer in layout['layers']:
            print(f"    - {layer['type']}: {layer['bbox']}")
        
        # Save template
        template = pipeline.layout_to_template(layout)
        output_path = f"templates/postero_{keywords.replace(' ', '_')}.json"
        pipeline.save_template(template, output_path)

def demo_with_llm():
    """Demo using LLM-based layout (requires model download)"""
    print("\n" + "="*60)
    print("DEMO 2: PosterO WITH LLM")
    print("="*60)
    
    # Check if model exists
    model_paths = [
        "./models/llama-3.1-8b",
        "./models/mistral-7b",
        "./models/qwen-7b"
    ]
    
    model_path = None
    for path in model_paths:
        if Path(path).exists():
            model_path = path
            break
    
    if not model_path:
        print("\n❌ No LLM model found!")
        print("\nTo use LLM, download a model first:")
        print("\n  Option 1 - LLaMA 3.1-8B (best quality):")
        print("    huggingface-cli download meta-llama/Meta-Llama-3.1-8B-Instruct --local-dir ./models/llama-3.1-8b")
        print("\n  Option 2 - Mistral 7B (no approval needed):")
        print("    huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ./models/mistral-7b")
        print("\n  Option 3 - Qwen 7B (no approval needed):")
        print("    huggingface-cli download Qwen/Qwen2-7B-Instruct --local-dir ./models/qwen-7b")
        print("\nSee USE_POSTERO_WITH_LLM.md for detailed instructions.")
        return
    
    print(f"\n✅ Found model: {model_path}")
    
    try:
        from postero_pipeline import PosterOPipeline
        
        print("\nInitializing PosterO with LLM...")
        pipeline = PosterOPipeline(
            llm_path=model_path,
            canvas_size=(720, 1080),
            use_official=True
        )
        
        # Generate layout
        keywords = "cyberpunk neon city"
        print(f"\nGenerating layout for: '{keywords}'")
        
        dummy_img = Image.new('RGB', (720, 1080), 'white')
        layout = pipeline.generate_layout(dummy_img, keywords, num_elements=3)
        
        print(f"\n✅ Generated {len(layout['layers'])} layers:")
        for layer in layout['layers']:
            print(f"    - {layer['type']}: {layer['bbox']}")
        
        # Save template
        template = pipeline.layout_to_template(layout)
        output_path = "templates/postero_llm_generated.json"
        pipeline.save_template(template, output_path)
        
        print(f"\n✅ Template saved: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure vLLM is installed:")
        print("  pip install vllm")

def demo_with_key2poster():
    """Demo integration with Key2Poster pipeline"""
    print("\n" + "="*60)
    print("DEMO 3: PosterO + Key2Poster Integration")
    print("="*60)
    
    try:
        from postero_pipeline import PosterOPipeline
        from pipeline import Key2PosterPipeline
        
        # Step 1: Generate layout with PosterO
        print("\nStep 1: Generating layout with PosterO...")
        postero = PosterOPipeline(canvas_size=(720, 1080), use_official=False)
        
        dummy_img = Image.new('RGB', (720, 1080), 'white')
        layout = postero.generate_layout(dummy_img, "anime love story", num_elements=3)
        template = postero.layout_to_template(layout)
        
        template_path = "templates/postero_for_key2poster.json"
        postero.save_template(template, template_path)
        print(f"  ✅ Layout saved: {template_path}")
        
        # Step 2: Generate poster with Key2Poster
        print("\nStep 2: Generating poster with Key2Poster...")
        print("  (This requires FLUX model and GPU)")
        
        print("\n  Usage:")
        print(f"    pipeline = Key2PosterPipeline(use_flux=True)")
        print(f"    image, brief, metrics = pipeline.generate_poster(")
        print(f"        'anime love story japanese',")
        print(f"        template_path='{template_path}',")
        print(f"        output_path='outputs/postero_poster.png'")
        print(f"    )")
        
        # Show template content
        print(f"\n  Template content:")
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        print(f"    Size: {template_data['size']}")
        print(f"    Layers: {len(template_data['layers'])}")
        for layer in template_data['layers']:
            print(f"      - {layer['name']}: {layer['bbox']}")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")

def main():
    print("\n" + "="*60)
    print("PosterO + LLM Integration Demo")
    print("="*60)
    
    # Demo 1: Without LLM (always works)
    demo_without_llm()
    
    # Demo 2: With LLM (requires model download)
    demo_with_llm()
    
    # Demo 3: Integration with Key2Poster
    demo_with_key2poster()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\n📖 For detailed instructions, see: USE_POSTERO_WITH_LLM.md")
    print("\n🚀 Quick Start:")
    print("  1. Download model: huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ./models/mistral-7b")
    print("  2. Install vLLM: pip install vllm")
    print("  3. Run this script again to test LLM integration")

if __name__ == "__main__":
    main()
