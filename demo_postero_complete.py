"""
Complete PosterO Demo - Shows both implementations
1. Generalized Layout (teammates' work)
2. Content-Aware Layout (your work)
"""
from PIL import Image
import json

def demo_generalized_layout():
    """Demo: Generalized Content-Aware Layout (PStylish7)"""
    print("\n" + "="*60)
    print("DEMO 1: Generalized Layout (7 Categories)")
    print("="*60)
    
    try:
        from src.postero_generalized import PosterOGeneralized
        
        gen = PosterOGeneralized(
            llm_path="./models/mistral-7b",
            dataset_root="./src/Dataset/PStylish7"
        )
        
        layout = gen.generate_layout(
            category="movie-poster",
            num_elements=3,
            sample_size=5
        )
        
        print(f"✅ Generated layout for movie-poster")
        print(f"   Elements: {len(layout['labels'])}")
        print(f"   Labels: {layout['labels']}")
        print(f"   Canvas: {layout['canvas_size']}")
        
        return layout
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("   Make sure PStylish7 dataset exists in src/Dataset/")
        return None

def demo_content_aware_layout():
    """Demo: Content-Aware Layout with Design Intent"""
    print("\n" + "="*60)
    print("DEMO 2: Content-Aware Layout (Design Intent Detection)")
    print("="*60)
    
    try:
        from src.postero_content_aware import PosterOContentAware
        
        pipeline = PosterOContentAware(
            llm_path="./models/mistral-7b",
            dataset_root="./datasets",
            intent_model_path=None,  # Use rule-based fallback
            canvas_size=(720, 1080)
        )
        
        # Create test image
        image = Image.new('RGB', (720, 1080), 'lightblue')
        
        layout = pipeline.generate_layout(
            image=image,
            keywords="cyberpunk neon city",
            num_elements=3
        )
        
        print(f"✅ Generated layout for 'cyberpunk neon city'")
        print(f"   Elements: {len(layout['labels'])}")
        print(f"   Intent regions: {len(layout['intent_regions'])}")
        print(f"   Canvas: {layout['canvas_size']}")
        
        return layout
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("   This is expected if LLM not available")
        return None

def demo_integration_with_key2poster():
    """Demo: Full integration with Key2Poster pipeline"""
    print("\n" + "="*60)
    print("DEMO 3: Integration with Key2Poster Pipeline")
    print("="*60)
    
    try:
        from src.postero_content_aware import PosterOContentAware
        from src.pipeline import Key2PosterPipeline
        
        # Step 1: Generate layout with PosterO
        print("\n[1/3] Generating layout with PosterO...")
        postero = PosterOContentAware(
            llm_path="./models/mistral-7b",
            dataset_root="./datasets",
            intent_model_path=None,
            canvas_size=(720, 1080)
        )
        
        dummy_img = Image.new('RGB', (720, 1080), 'white')
        layout = postero.generate_layout(dummy_img, "anime love story", num_elements=3)
        template = postero.layout_to_template(layout)
        
        # Step 2: Save template
        print("[2/3] Saving template...")
        template_path = 'templates/postero_demo.json'
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"   ✓ Saved to {template_path}")
        
        # Step 3: Generate poster with FLUX
        print("[3/3] Generating poster with FLUX...")
        key2poster = Key2PosterPipeline(use_flux=True)
        poster, brief, _ = key2poster.generate_poster(
            "anime love story japanese",
            template_path=template_path,
            output_path='outputs/postero_demo.png',
            seed=42
        )
        
        print(f"\n✅ Complete pipeline finished!")
        print(f"   Output: {brief['output_path']}")
        
        return poster
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("   This requires FLUX model and GPU")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PosterO Complete Demo")
    print("="*60)
    print("\nThis demo shows:")
    print("1. Generalized Layout (teammates' implementation)")
    print("2. Content-Aware Layout (your implementation)")
    print("3. Full integration with Key2Poster")
    
    # Run demos
    layout1 = demo_generalized_layout()
    layout2 = demo_content_aware_layout()
    poster = demo_integration_with_key2poster()
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    if layout1:
        print("✅ Generalized Layout: Working")
    else:
        print("⚠ Generalized Layout: Check PStylish7 dataset")
    
    if layout2:
        print("✅ Content-Aware Layout: Working")
    else:
        print("⚠ Content-Aware Layout: Check LLM setup")
    
    if poster:
        print("✅ Full Pipeline: Working")
    else:
        print("⚠ Full Pipeline: Check FLUX setup")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Test generalized: python test_postero_generalized.py")
    print("2. Test content-aware: python test_postero_content_aware.py")
    print("3. Setup models: python setup_postero_content_aware.py")
    print("4. Read docs: POSTERO_IMPLEMENTATION_STATUS.md")
