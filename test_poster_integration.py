"""Test integration of cinematic text overlay with poster generation"""
from PIL import Image
from src.cinematic_text_overlay import CinematicTextOverlay
from pathlib import Path

def test_with_existing_posters():
    """Test overlay on existing generated posters"""
    print("=" * 60)
    print("TESTING CINEMATIC TEXT OVERLAY INTEGRATION")
    print("=" * 60)
    
    overlay = CinematicTextOverlay()
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        print("\n❌ No outputs directory found. Generate posters first:")
        print("   python run_pipeline.py \"space adventure\" --genre-lora --seed 42")
        return
    
    posters = list(outputs_dir.glob("*.png"))
    if not posters:
        print("\n❌ No posters found in outputs/. Generate posters first:")
        print("   python run_pipeline.py \"dark horror\" --genre-lora --seed 123")
        return
    
    print(f"\n✓ Found {len(posters)} poster(s) in outputs/")
    
    test_dir = Path("outputs/integration_test")
    test_dir.mkdir(exist_ok=True)
    
    test_cases = [
        {"title": "EPIC ADVENTURE", "genre": "epic", "position": "bottom"},
        {"title": "DARK HORROR", "genre": "horror", "position": "center"},
        {"title": "CYBER FUTURE", "genre": "scifi", "position": "bottom"},
        {"title": "LOVE STORY", "genre": "romance", "position": "bottom"},
        {"title": "ACTION HERO", "genre": "action", "position": "bottom"},
    ]
    
    poster = Image.open(posters[0])
    print(f"\nUsing poster: {posters[0].name}")
    print(f"Size: {poster.size}")
    
    print("\n" + "-" * 60)
    print("Testing different genres and styles...")
    print("-" * 60)
    
    for i, test in enumerate(test_cases):
        try:
            result = overlay.add_text(
                poster,
                test["title"],
                genre=test["genre"],
                position=test["position"],
                auto_adapt=True
            )
            
            output_path = test_dir / f"test_{i}_{test['genre']}.png"
            result.save(output_path)
            
            rules = overlay.GENRE_FONT_RULES.get(test["genre"], {})
            font_cat = rules.get("category", "N/A")
            
            print(f"✓ {test['title']:20} | Genre: {test['genre']:12} | Font: {font_cat:12} | {output_path.name}")
            
        except Exception as e:
            print(f"✗ {test['title']:20} | Error: {str(e)}")
    
    print("\n" + "-" * 60)
    print("Testing font categories...")
    print("-" * 60)
    
    print(f"\nAvailable fonts: {len(overlay.available_fonts)}")
    for font_name in list(overlay.available_fonts.keys())[:5]:
        print(f"  - {font_name}")
    if len(overlay.available_fonts) > 5:
        print(f"  ... and {len(overlay.available_fonts) - 5} more")
    
    print(f"\nFont categories:")
    for category, fonts in overlay.categorized_fonts.items():
        if fonts:
            print(f"  {category}: {len(fonts)} font(s)")
    
    print("\n" + "=" * 60)
    print(f"✅ Integration test complete!")
    print(f"Results saved to: {test_dir}/")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("1. Check outputs/integration_test/ for results")
    print("2. Launch UI: python app_text_overlay.py")
    print("3. Generate new poster: python run_pipeline.py \"keywords\" --genre-lora")

def quick_test():
    """Quick test with synthetic poster"""
    print("\n" + "=" * 60)
    print("QUICK TEST - Creating synthetic poster")
    print("=" * 60)
    
    from PIL import ImageDraw
    
    img = Image.new('RGB', (512, 768), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    for y in range(768):
        intensity = int(30 + (y / 768) * 100)
        draw.rectangle([(0, y), (512, y+1)], fill=(intensity//3, intensity//4, intensity))
    
    overlay = CinematicTextOverlay()
    
    test_dir = Path("outputs/integration_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    genres = ["action", "horror", "scifi", "drama", "epic"]
    
    print("\nGenerating test overlays...")
    for genre in genres:
        result = overlay.add_text(img, f"{genre.upper()} MOVIE", genre=genre, auto_adapt=True)
        result.save(test_dir / f"quick_{genre}.png")
        print(f"✓ Created quick_{genre}.png")
    
    print(f"\n✅ Quick test complete! Check {test_dir}/")

if __name__ == "__main__":
    import sys
    
    if "--quick" in sys.argv:
        quick_test()
    else:
        test_with_existing_posters()
        
        if input("\nRun quick test too? (y/n): ").lower() == 'y':
            quick_test()
