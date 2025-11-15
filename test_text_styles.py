"""Test text styling on existing images"""
from PIL import Image
from src.text_overlay import TextOverlay
from pathlib import Path

def test_all_styles():
    """Test all genre styles on a sample image"""
    overlay = TextOverlay()
    
    # Create a sample image if none exists
    output_dir = Path("outputs/text_style_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find an existing poster or create blank
    sample_images = list(Path("outputs").glob("*.png"))
    if sample_images:
        base_image = Image.open(sample_images[0])
        print(f"Using existing image: {sample_images[0]}")
    else:
        # Create blank poster
        base_image = Image.new('RGB', (720, 1280), color=(50, 50, 50))
        print("Created blank test image")
    
    # Test each style
    styles = ["action", "horror", "scifi", "drama", "comedy", "thriller", "fantasy", "romance", "cinematic"]
    
    print("\nGenerating styled text samples...")
    for style in styles:
        try:
            styled_image = overlay.add_title(base_image.copy(), "MOVIE TITLE", genre=style)
            output_path = output_dir / f"style_{style}.png"
            styled_image.save(output_path)
            print(f"  [OK] {style.upper():12} -> {output_path}")
        except Exception as e:
            print(f"  [ERROR] {style}: {e}")
    
    print(f"\n[SUCCESS] Test complete! Check {output_dir}/")

if __name__ == "__main__":
    test_all_styles()
