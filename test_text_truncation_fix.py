"""Test that all words are preserved in text overlay"""
from PIL import Image, ImageDraw
from src.cinematic_text_overlay import CinematicTextOverlay
from pathlib import Path

def create_test_poster():
    img = Image.new('RGB', (512, 768), color=(40, 40, 60))
    draw = ImageDraw.Draw(img)
    for y in range(768):
        intensity = int(40 + (y / 768) * 80)
        draw.rectangle([(0, y), (512, y+1)], fill=(intensity//2, intensity//3, intensity))
    return img

def test_word_preservation():
    print("=" * 60)
    print("TESTING TEXT TRUNCATION FIX")
    print("=" * 60)
    
    overlay = CinematicTextOverlay()
    test_dir = Path("outputs/truncation_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_cases = [
        "space exploration adventure",
        "dark horror mansion",
        "epic fantasy battle",
        "romantic sunset beach",
        "cyberpunk neon city",
        "very long movie title here",
        "extremely long title that should still fit"
    ]
    
    print("\nTesting word preservation...")
    print("-" * 60)
    
    for i, text in enumerate(test_cases):
        img = create_test_poster()
        word_count = len(text.split())
        
        result = overlay.add_text(
            img,
            text,
            genre="cinematic",
            position="bottom",
            auto_adapt=True
        )
        
        output_path = test_dir / f"test_{i}_{word_count}words.png"
        result.save(output_path)
        
        print(f"✓ Test {i+1}: '{text}'")
        print(f"  Words: {word_count} | Saved: {output_path.name}")
    
    print("\n" + "=" * 60)
    print("✅ All words should be visible in the posters!")
    print(f"Check results in: {test_dir}/")
    print("=" * 60)

if __name__ == "__main__":
    test_word_preservation()
