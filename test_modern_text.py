"""Test Modern Text Rendering Methods"""
from src.pipeline_modern import ModernKey2PosterPipeline
from src.pipeline import Key2PosterPipeline
from PIL import Image
import time

def test_diffusion_text():
    """Test FLUX diffusion-based text"""
    print("\n" + "="*60)
    print("TEST 1: FLUX Diffusion Text Rendering")
    print("="*60)
    
    try:
        pipeline = ModernKey2PosterPipeline(
            text_method='diffusion',
            use_flux=True,
            genre_lora=True
        )
        
        test_cases = [
            ("cyberpunk neon city", "scifi"),
            ("dark horror mansion", "horror"),
            ("space adventure epic", "action")
        ]
        
        for i, (keywords, expected_genre) in enumerate(test_cases):
            print(f"\n--- Test Case {i+1}: {keywords} ---")
            start = time.time()
            
            image, brief, metrics = pipeline.generate_poster(
                keywords,
                output_path=f"outputs/modern_text/diffusion_{i}_{keywords.replace(' ', '_')}.png",
                seed=42+i
            )
            
            elapsed = time.time() - start
            print(f"✓ Generated in {elapsed:.1f}s")
            print(f"  Aesthetic: {metrics['aesthetic']['overall']:.3f}")
        
        print("\n✅ FLUX diffusion text test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ FLUX diffusion text test FAILED: {e}")
        return False


def test_hybrid_text():
    """Test hybrid text rendering"""
    print("\n" + "="*60)
    print("TEST 2: Hybrid Text Rendering")
    print("="*60)
    
    try:
        pipeline = ModernKey2PosterPipeline(
            text_method='hybrid',
            use_flux=True
        )
        
        keywords = "romantic sunset beach"
        print(f"\nTesting: {keywords}")
        
        image, brief, metrics = pipeline.generate_poster(
            keywords,
            output_path="outputs/modern_text/hybrid_test.png",
            seed=42
        )
        
        print("\n✅ Hybrid text test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Hybrid text test FAILED: {e}")
        return False


def compare_old_vs_new():
    """Compare old PIL method vs new diffusion method"""
    print("\n" + "="*60)
    print("TEST 3: Old vs New Comparison")
    print("="*60)
    
    keywords = "space exploration adventure"
    
    # Old method (PIL)
    print("\n--- Old Method (PIL) ---")
    try:
        old_pipeline = Key2PosterPipeline(
            use_flux=True,
            add_title=True,
            genre_lora=True
        )
        
        start = time.time()
        old_image, _, old_metrics = old_pipeline.generate_poster(
            keywords,
            output_path="outputs/modern_text/old_pil_method.png",
            seed=42
        )
        old_time = time.time() - start
        
        print(f"✓ Old method: {old_time:.1f}s")
        print(f"  Aesthetic: {old_metrics['aesthetic']['overall']:.3f}")
        
    except Exception as e:
        print(f"❌ Old method failed: {e}")
        old_time = None
    
    # New method (FLUX)
    print("\n--- New Method (FLUX Diffusion) ---")
    try:
        new_pipeline = ModernKey2PosterPipeline(
            text_method='diffusion',
            use_flux=True,
            genre_lora=True
        )
        
        start = time.time()
        new_image, _, new_metrics = new_pipeline.generate_poster(
            keywords,
            output_path="outputs/modern_text/new_flux_method.png",
            seed=42
        )
        new_time = time.time() - start
        
        print(f"✓ New method: {new_time:.1f}s")
        print(f"  Aesthetic: {new_metrics['aesthetic']['overall']:.3f}")
        
    except Exception as e:
        print(f"❌ New method failed: {e}")
        new_time = None
    
    # Comparison
    print("\n" + "-"*60)
    print("COMPARISON RESULTS:")
    print("-"*60)
    
    if old_time and new_time:
        print(f"Old (PIL):        {old_time:.1f}s | Aesthetic: {old_metrics['aesthetic']['overall']:.3f}")
        print(f"New (FLUX):       {new_time:.1f}s | Aesthetic: {new_metrics['aesthetic']['overall']:.3f}")
        
        if new_metrics['aesthetic']['overall'] > old_metrics['aesthetic']['overall']:
            print("\n✅ New method has BETTER aesthetic quality")
        else:
            print("\n⚠️ Old method has better aesthetic (unexpected)")
        
        print(f"\nSpeed difference: {abs(new_time - old_time):.1f}s")
    
    return True


def test_genre_styles():
    """Test all genre-specific text styles"""
    print("\n" + "="*60)
    print("TEST 4: Genre-Specific Text Styles")
    print("="*60)
    
    try:
        pipeline = ModernKey2PosterPipeline(
            text_method='diffusion',
            use_flux=True,
            genre_lora=True
        )
        
        genre_tests = {
            'action': 'explosive car chase',
            'horror': 'haunted dark mansion',
            'scifi': 'futuristic space station',
            'romance': 'sunset beach love',
            'comedy': 'funny party chaos',
            'fantasy': 'magical dragon realm',
            'thriller': 'mysterious crime scene',
            'drama': 'emotional family story'
        }
        
        for genre, keywords in genre_tests.items():
            print(f"\n--- Testing {genre.upper()} style ---")
            
            image, _, _ = pipeline.generate_poster(
                keywords,
                output_path=f"outputs/modern_text/genre_{genre}.png",
                seed=42
            )
            
            print(f"✓ {genre} style generated")
        
        print("\n✅ All genre styles test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Genre styles test FAILED: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MODERN TEXT RENDERING TEST SUITE")
    print("="*60)
    
    # Create output directory
    from pathlib import Path
    Path("outputs/modern_text").mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Run tests
    print("\n🧪 Running tests...")
    
    # Test 1: FLUX diffusion (main test)
    results.append(("FLUX Diffusion", test_diffusion_text()))
    
    # Test 2: Hybrid method
    results.append(("Hybrid Method", test_hybrid_text()))
    
    # Test 3: Comparison
    results.append(("Old vs New", compare_old_vs_new()))
    
    # Test 4: Genre styles
    results.append(("Genre Styles", test_genre_styles()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed! Modern text rendering is working.")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
    
    print("\n📁 Check outputs/modern_text/ for generated posters")
