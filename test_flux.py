"""Test FLUX.1 poster generation"""
from src.visual_generator_flux import VisualGeneratorFlux
from pathlib import Path

def test_flux():
    print("\n" + "="*60)
    print("TESTING FLUX.1 POSTER GENERATION")
    print("="*60)
    
    # Initialize
    print("\n[1] Initializing FLUX.1...")
    generator = VisualGeneratorFlux(model_id="black-forest-labs/FLUX.1-schnell")
    
    # Test cases
    test_cases = [
        "cyberpunk neon city at night",
        "dark horror mansion in fog",
        "space adventure with planets"
    ]
    
    output_dir = Path("outputs/flux_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, prompt in enumerate(test_cases):
        print(f"\n[{i+2}] Generating: {prompt}")
        
        image = generator.generate(
            prompt=prompt,
            width=720,
            height=1280,
            num_inference_steps=4,  # Fast mode
            seed=42 + i
        )
        
        output_path = output_dir / f"flux_{i:02d}_{prompt[:20].replace(' ', '_')}.png"
        image.save(output_path)
        print(f"    ✓ Saved: {output_path}")
    
    print("\n" + "="*60)
    print("✅ FLUX.1 TEST COMPLETE!")
    print("="*60)
    print(f"\nGenerated files in: {output_dir}")
    print("\nNext steps:")
    print("1. Compare quality with SD v1.5")
    print("2. Integrate into pipeline")
    print("3. Try FLUX.1-dev for higher quality")

if __name__ == "__main__":
    try:
        test_flux()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
