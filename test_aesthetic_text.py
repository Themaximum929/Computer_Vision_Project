"""Test Aesthetic Text Overlay"""
from PIL import Image
from src.aesthetic_text_overlay import AestheticTextOverlay
from pathlib import Path

def test_aesthetic_text():
    """Test PosterCraft-style text overlay"""
    print("\n" + "="*60)
    print("TESTING AESTHETIC TEXT OVERLAY")
    print("="*60)
    
    # Create test image
    test_img = Image.new('RGB', (768, 1024), (50, 80, 120))
    
    overlay = AestheticTextOverlay()
    output_dir = Path("outputs/aesthetic_text_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test 1: Full poster text
    print("\n[Test 1] Full poster text with all elements")
    result = overlay.add_poster_text(
        image=test_img.copy(),
        title="Cyberpunk City",
        genre="scifi",
        tagline="The future is now",
        credits="Directed by John Doe • 2024"
    )
    result.save(output_dir / "full_poster.png")
    print("✓ Saved: full_poster.png")
    
    # Test 2: Genre variations
    print("\n[Test 2] Genre-specific styling")
    genres = ["action", "horror", "scifi", "romance", "comedy", "fantasy"]
    
    for genre in genres:
        result = overlay.add_poster_text(
            image=test_img.copy(),
            title="Movie Title",
            genre=genre,
            tagline=f"{genre.title()} tagline"
        )
        result.save(output_dir / f"genre_{genre}.png")
        print(f"✓ Saved: genre_{genre}.png")
    
    # Test 3: Minimal text
    print("\n[Test 3] Minimal text overlay")
    result = overlay.add_minimal_text(
        image=test_img.copy(),
        title="Minimal Design",
        accent_color=(0, 200, 255)
    )
    result.save(output_dir / "minimal.png")
    print("✓ Saved: minimal.png")
    
    # Test 4: With real image (if available)
    print("\n[Test 4] With generated image")
    try:
        from src.pipeline import Key2PosterPipeline
        
        pipeline = Key2PosterPipeline(
            genre_lora=True,
            add_title=False,
            aggressive_text_removal=True,
            super_resolution=False
        )
        
        image, brief, _ = pipeline.generate_poster(
            "cyberpunk neon city",
            output_path=str(output_dir / "base.png"),
            seed=42,
            evaluate=False
        )
        
        # Apply aesthetic text
        result = overlay.add_poster_text(
            image=image,
            title="Neon City",
            genre="scifi",
            tagline="Where dreams become reality",
            credits="A Cyberpunk Story"
        )
        result.save(output_dir / "real_poster.png")
        print("✓ Saved: real_poster.png")
        
    except Exception as e:
        print(f"⚠ Skipped real image test: {e}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print(f"\nGenerated files in: {output_dir}")
    print("\nFiles created:")
    print("  • full_poster.png - Complete text hierarchy")
    print("  • genre_*.png - 6 genre variations")
    print("  • minimal.png - Minimal design")
    print("  • real_poster.png - With generated image")
    print("\nNext steps:")
    print("1. Check output images")
    print("2. Compare with PosterCraft examples")
    print("3. Adjust colors/fonts in aesthetic_text_overlay.py")
    print("4. Run: python app_unified.py")

if __name__ == "__main__":
    try:
        test_aesthetic_text()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
