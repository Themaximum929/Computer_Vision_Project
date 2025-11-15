"""Quick test of advanced text styling without full pipeline"""
from PIL import Image
from src.advanced_text_styler import AdvancedTextStyler

# Create test background
img = Image.new('RGB', (720, 1280), (20, 30, 50))

styler = AdvancedTextStyler()

# Test all modes
tests = [
    ("NEURAL STYLE", "horror", "neural"),
    ("DYNAMIC GLOW", "scifi", "dynamic"),
    ("CURVED LAYOUT", "action", "layout"),
]

for title, genre, mode in tests:
    result = styler.add_styled_title(img, title, genre, mode)
    result.save(f"test_{mode}.png")
    print(f"✓ {mode} mode: test_{mode}.png")

print("\nDone! Check test_*.png files")
