"""Compare edge-based vs OCR-based text removal with resolution enhancement"""
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.aggressive_text_remover import AggressiveTextRemover
from src.super_resolution import SuperResolution
from preprocess_with_ocr import remove_text_ocr

# Download poster
url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
response = requests.get(url, timeout=30)
image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
image.save("outputs/original.png")
print(f"Original: {image.size}\n")

edge_remover = AggressiveTextRemover()
sr = SuperResolution()

# Test 1: Edge-based removal
print("[1] Edge-based text removal...")
cleaned1, found1 = edge_remover.remove_text(image.copy(), iterations=3)
cleaned1.save("outputs/compare1_edge_based.png")
print(f"    Text found: {found1}\n")

# Test 2: OCR-based removal
print("[2] OCR-based text removal...")
cleaned2, found2 = remove_text_ocr(image.copy())
cleaned2.save("outputs/compare2_ocr_based.png")
print(f"    Text found: {found2}\n")

# Test 3: Edge + Enhancement
print("[3] Edge-based + Super-resolution...")
enhanced = sr.enhance_details(image.copy())
cleaned3, found3 = edge_remover.remove_text(enhanced, iterations=3)
cleaned3.save("outputs/compare3_edge_enhanced.png")
print(f"    Text found: {found3}\n")

# Test 4: OCR + Enhancement
print("[4] OCR-based + Super-resolution...")
enhanced2 = sr.enhance_details(image.copy())
cleaned4, found4 = remove_text_ocr(enhanced2)
cleaned4.save("outputs/compare4_ocr_enhanced.png")
print(f"    Text found: {found4}\n")

print("="*60)
print("COMPARISON RESULTS:")
print("  compare1_edge_based.png - Edge detection only")
print("  compare2_ocr_based.png - OCR detection only")
print("  compare3_edge_enhanced.png - Edge + Enhancement")
print("  compare4_ocr_enhanced.png - OCR + Enhancement")
print("="*60)
print("\nCheck outputs/ to see which method removes text best!")
