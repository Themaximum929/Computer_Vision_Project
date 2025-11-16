"""Test Unified Pipeline"""
from src.unified_pipeline import UnifiedPosterPipeline
from pathlib import Path

def test_unified_pipeline():
    """Test complete unified pipeline"""
    print("\n" + "="*60)
    print("TESTING UNIFIED PIPELINE")
    print("="*60)
    
    # Initialize
    pipeline = UnifiedPosterPipeline(use_lora=True, genre_detection=True)
    
    # Test cases
    test_cases = [
        ("cyberpunk neon city", "modern"),
        ("dark horror mansion", "classic"),
        ("space adventure epic", "minimal"),
    ]
    
    output_dir = Path("outputs/unified_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, (keywords, template) in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Test {i+1}/{len(test_cases)}: {keywords}")
        print(f"{'='*60}")
        
        # Generate
        result = pipeline.generate(
            keywords=keywords,
            template=template,
            add_effects=True,
            seed=42 + i
        )
        
        # Save
        output_path = output_dir / f"test_{i:02d}_{keywords.replace(' ', '_')}.png"
        pipeline.save(result, str(output_path))
        
        # Verify
        assert result['image'] is not None, "Image should be generated"
        assert result['genre'] is not None, "Genre should be detected"
        assert len(result['palette']) == 5, "Should have 5 colors"
        
        print(f"\n✅ Test {i+1} passed!")
        print(f"   Genre: {result['genre']}")
        print(f"   Mood: {result['mood']}")
        print(f"   Time: {result['time']:.1f}s")
    
    print(f"\n{'='*60}")
    print(f"✅ ALL TESTS PASSED!")
    print(f"{'='*60}")
    print(f"\nGenerated files in: {output_dir}")
    print(f"\nNext steps:")
    print(f"1. Check outputs in {output_dir}")
    print(f"2. Run: python app_unified.py")
    print(f"3. Compare with original pipeline")

if __name__ == "__main__":
    try:
        test_unified_pipeline()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
