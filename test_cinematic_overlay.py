from PIL import Image, ImageDraw
import numpy as np
from src.cinematic_text_overlay import CinematicTextOverlay
from pathlib import Path

def create_test_poster(color, name):
    """Create a test poster with gradient background"""
    w, h = 512, 768
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    
    for y in range(h):
        intensity = int(color * (1 - y/h))
        draw.rectangle([(0, y), (w, y+1)], fill=(intensity, intensity//2, intensity//3))
    
    output_dir = Path("outputs/test_overlays")
    output_dir.mkdir(parents=True, exist_ok=True)
    img.save(output_dir / f"base_{name}.png")
    return img

def test_auto_adaptation():
    """Test automatic font and color selection"""
    print("Testing automatic adaptation...")
    overlay = CinematicTextOverlay()
    
    test_cases = [
        (200, "bright", "action"),
        (50, "dark", "horror"),
        (150, "medium", "scifi"),
    ]
    
    for brightness, name, genre in test_cases:
        img = create_test_poster(brightness, name)
        result = overlay.add_text(img, "EPIC MOVIE", genre=genre, auto_adapt=True)
        result.save(f"outputs/test_overlays/auto_{name}_{genre}.png")
        print(f"✓ Created auto_{name}_{genre}.png")

def test_manual_customization():
    """Test manual font and color customization"""
    print("\nTesting manual customization...")
    overlay = CinematicTextOverlay()
    img = create_test_poster(100, "custom")
    
    configs = [
        {"font_size": 60, "color": (255, 0, 0), "position": "top", "name": "red_top"},
        {"font_size": 100, "color": (0, 255, 255), "position": "center", "name": "cyan_center"},
        {"font_size": 80, "color": (255, 215, 0), "position": "bottom", "stroke_width": 5, "name": "gold_bottom"},
    ]
    
    for config in configs:
        name = config.pop("name")
        result = overlay.add_text(img, "CUSTOM TEXT", auto_adapt=False, **config)
        result.save(f"outputs/test_overlays/manual_{name}.png")
        print(f"✓ Created manual_{name}.png")

def test_genre_styles():
    """Test all genre-specific styles with font categories"""
    print("\nTesting genre styles with font categories...")
    overlay = CinematicTextOverlay()
    img = create_test_poster(80, "genres")
    
    genres = ["action", "horror", "scifi", "drama", "comedy", "thriller", 
              "fantasy", "romance", "epic", "historical", "modern", "minimalist"]
    
    for genre in genres:
        result = overlay.add_text(img, genre.upper(), genre=genre, auto_adapt=True)
        result.save(f"outputs/test_overlays/genre_{genre}.png")
        
        rules = overlay.GENRE_FONT_RULES.get(genre, {})
        cat = rules.get("category", "N/A")
        print(f"✓ Created genre_{genre}.png (Font: {cat})")

def test_text_bounds():
    """Test text boundary handling"""
    print("\nTesting text boundary handling...")
    overlay = CinematicTextOverlay()
    img = create_test_poster(120, "bounds")
    
    long_texts = [
        "VERY LONG MOVIE TITLE HERE",
        "SHORT",
        "MEDIUM LENGTH TITLE"
    ]
    
    for i, text in enumerate(long_texts):
        result = overlay.add_text(img, text, auto_adapt=True, genre="cinematic")
        result.save(f"outputs/test_overlays/bounds_{i}.png")
        print(f"✓ Created bounds_{i}.png with text: {text}")

def test_font_categories():
    """Test font category system"""
    print("\nTesting font categories...")
    overlay = CinematicTextOverlay()
    
    print(f"\nAvailable fonts by category:")
    for category, fonts in overlay.categorized_fonts.items():
        if fonts:
            print(f"  {category}: {', '.join(fonts)}")
    
    print(f"\nGenre → Font Category Mapping:")
    for genre, rules in overlay.GENRE_FONT_RULES.items():
        print(f"  {genre}: {rules['category']} (fallback: {rules['fallback']})")

def test_with_real_poster():
    """Test with existing poster if available"""
    print("\nTesting with real poster...")
    overlay = CinematicTextOverlay()
    
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        posters = list(outputs_dir.glob("*.png"))
        if posters:
            img = Image.open(posters[0])
            result = overlay.add_text(img, "REMASTERED", genre="cinematic", auto_adapt=True)
            result.save("outputs/test_overlays/real_poster_overlay.png")
            print(f"✓ Created real_poster_overlay.png")
            return
    
    print("⚠ No existing posters found, skipping real poster test")

def main():
    print("=" * 60)
    print("CINEMATIC TEXT OVERLAY TEST SUITE")
    print("=" * 60)
    
    test_font_categories()
    test_auto_adaptation()
    test_manual_customization()
    test_genre_styles()
    test_text_bounds()
    test_with_real_poster()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print(f"Results saved to: outputs/test_overlays/")
    print("=" * 60)

if __name__ == "__main__":
    main()
