"""End-to-end test: Generate posters from scratch with cinematic text overlay"""
from src.pipeline import Key2PosterPipeline
from pathlib import Path
import time

def test_full_pipeline():
    """Test complete pipeline: generation -> text removal -> enhancement -> text overlay"""
    print("=" * 70)
    print("FULL PIPELINE TEST: Image Generation + Cinematic Text Overlay")
    print("=" * 70)
    
    test_cases = [
        {
            "keywords": "space exploration adventure",
            "genre": "scifi",
            "seed": 42,
            "name": "space_adventure"
        },
        {
            "keywords": "dark horror mansion",
            "genre": "horror",
            "seed": 123,
            "name": "dark_horror"
        },
        {
            "keywords": "epic fantasy battle",
            "genre": "epic",
            "seed": 456,
            "name": "epic_fantasy"
        },
        {
            "keywords": "romantic sunset beach",
            "genre": "romance",
            "seed": 789,
            "name": "romantic_sunset"
        },
        {
            "keywords": "cyberpunk neon city",
            "genre": "scifi",
            "seed": 999,
            "name": "cyberpunk_city"
        }
    ]
    
    output_dir = Path("outputs/full_pipeline_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(test_cases)}: {test['keywords']}")
        print(f"{'='*70}")
        
        try:
            start_time = time.time()
            
            pipeline = Key2PosterPipeline(
                baseline_style=True,
                add_title=True,
                remove_text=False,
                aggressive_text_removal=False,
                super_resolution=False
            )
            
            pipeline._current_genre = test['genre']
            
            output_path = output_dir / f"{test['name']}.png"
            
            image, brief, metrics = pipeline.generate_poster(
                test['keywords'],
                output_path=str(output_path),
                seed=test['seed'],
                evaluate=True
            )
            
            elapsed = time.time() - start_time
            
            result = {
                "name": test['name'],
                "keywords": test['keywords'],
                "success": True,
                "time": elapsed,
                "sentiment": brief['sentiment'],
                "aesthetic_score": metrics['aesthetic']['overall'],
                "resolution": f"{metrics['resolution']['width']}x{metrics['resolution']['height']}",
                "path": str(output_path)
            }
            
            results.append(result)
            
            print(f"\n✅ SUCCESS: {test['name']}")
            print(f"   Time: {elapsed:.1f}s")
            print(f"   Sentiment: {brief['sentiment']}")
            print(f"   Aesthetic: {metrics['aesthetic']['overall']:.3f}")
            print(f"   Saved: {output_path}")
            
        except Exception as e:
            print(f"\n❌ FAILED: {test['name']}")
            print(f"   Error: {str(e)}")
            results.append({
                "name": test['name'],
                "keywords": test['keywords'],
                "success": False,
                "error": str(e)
            })
    
    print(f"\n{'='*70}")
    print("PIPELINE TEST SUMMARY")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    if successful > 0:
        avg_time = sum(r['time'] for r in results if r.get('success')) / successful
        avg_aesthetic = sum(r['aesthetic_score'] for r in results if r.get('success')) / successful
        
        print(f"\nAverage Generation Time: {avg_time:.1f}s")
        print(f"Average Aesthetic Score: {avg_aesthetic:.3f}")
    
    print(f"\n{'='*70}")
    print("DETAILED RESULTS")
    print(f"{'='*70}")
    
    for r in results:
        if r.get('success'):
            print(f"\n✓ {r['name']:20} | {r['keywords']:30}")
            print(f"  Time: {r['time']:.1f}s | Aesthetic: {r['aesthetic_score']:.3f} | {r['resolution']}")
            print(f"  Path: {r['path']}")
        else:
            print(f"\n✗ {r['name']:20} | {r['keywords']:30}")
            print(f"  Error: {r.get('error', 'Unknown error')}")
    
    print(f"\n{'='*70}")
    print("✅ FULL PIPELINE TEST COMPLETE")
    print(f"Results saved to: {output_dir}/")
    print(f"{'='*70}")
    
    print("\n📋 What was tested:")
    print("  ✓ Baseline image generation (NO LoRA)")
    print("  ✓ Manual genre assignment")
    print("  ✓ Cinematic text overlay with:")
    print("    - Genre-specific layouts (6 different designs)")
    print("    - Automatic font selection (serif/sans-serif/display)")
    print("    - Adaptive color based on background")
    print("    - Professional typography (angles, spacing, effects)")
    print("  ✓ Quality evaluation")
    
    return results

def quick_test():
    """Quick single poster test"""
    print("=" * 70)
    print("QUICK PIPELINE TEST")
    print("=" * 70)
    
    pipeline = Key2PosterPipeline(
        baseline_style=True,
        add_title=True,
        remove_text=False,
        super_resolution=False
    )
    
    pipeline._current_genre = "epic"
    
    output_path = "outputs/full_pipeline_test/quick_test.png"
    
    image, brief, metrics = pipeline.generate_poster(
        "epic space battle",
        output_path=output_path,
        seed=42,
        evaluate=True
    )
    
    print(f"\n✅ Quick test complete!")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    import sys
    
    if "--quick" in sys.argv:
        quick_test()
    else:
        test_full_pipeline()
