"""Test text boundary handling to ensure no overflow"""
from PIL import Image, ImageDraw
from src.cinematic_text_overlay import CinematicTextOverlay
from pathlib import Path

def create_test_poster():
    """Create test poster with visible borders"""
    img = Image.new('RGB', (512, 768), color=(40, 40, 60))
    draw = ImageDraw.Draw(img)
    
    for y in range(768):
        intensity = int(40 + (y / 768) * 80)
        draw.rectangle([(0, y), (512, y+1)], fill=(intensity//2, intensity//3, intensity))
    
    draw.rectangle([(0, 0), (511, 767)], outline=(255, 0, 0), width=3)
    draw.rectangle([(10, 10), (501, 757)], outline=(255, 255, 0), width=1)
    
    return img

def test_overflow_scenarios():
    """Test various text lengths and positions"""
    print("=" * 60)
    print("TESTING TEXT BOUNDARY HANDLING")
    print("=" * 60)
    
    overlay = CinematicTextOverlay()
    test_dir = Path("outputs/bounds_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_cases = [
        {"text": "SHORT", "position": "bottom", "name": "short_bottom"},
        {"text": "MEDIUM LENGTH TITLE", "position": "bottom", "name": "medium_bottom"},
        {"text": "VERY LONG MOVIE TITLE HERE", "position": "bottom", "name": "long_bottom"},
        {"text": "EXTREMELY LONG TITLE THAT SHOULD FIT", "position": "bottom", "name": "extreme_bottom"},
        {"text": "TOP TITLE", "position": "top", "name": "short_top"},
        {"text": "CENTER POSITIONED TEXT", "position": "center", "name": "medium_center"},
        {"text": "EPIC ADVENTURE STORY", "position": "bottom", "name": "epic_bottom"},
    ]
    
    print("\nTesting text overflow prevention...")
    print("-" * 60)
    
    for test in test_cases:
        img = create_test_poster()
        
        try:
            result = overlay.add_text(
                img,
                test["text"],
                position=test["position"],
                genre="cinematic",
                auto_adapt=True
            )
            
            output_path = test_dir / f"{test['name']}.png"
            result.save(output_path)
            
            print(f"✓ {test['name']:20} | Text: '{test['text'][:30]}' | Position: {test['position']}")
            
        except Exception as e:
            print(f"✗ {test['name']:20} | Error: {str(e)}")
    
    print("\n" + "-" * 60)
    print("Testing with different genres...")
    print("-" * 60)
    
    genres = ["action", "horror", "scifi", "epic"]
    for genre in genres:
        img = create_test_poster()
        result = overlay.add_text(img, f"{genre.upper()} MOVIE", genre=genre, position="bottom", auto_adapt=True)
        result.save(test_dir / f"genre_{genre}.png")
        print(f"✓ genre_{genre:10} | Genre-specific styling applied")
    
    print("\n" + "=" * 60)
    print("✅ Boundary test complete!")
    print(f"Check results in: {test_dir}/")
    print("Red border = poster edge")
    print("Yellow border = safe zone")
    print("Text should stay within yellow border")
    print("=" * 60)

if __name__ == "__main__":
    test_overflow_scenarios()
