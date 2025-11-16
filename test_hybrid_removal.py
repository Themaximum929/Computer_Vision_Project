"""Test hybrid text removal vs individual methods"""
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from src.aggressive_text_remover import AggressiveTextRemover
from src.hybrid_text_remover import HybridTextRemover
from preprocess_with_ocr import remove_text_ocr

url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
response = requests.get(url, timeout=30)
image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
image.save("outputs/final_original.png")

edge_remover = AggressiveTextRemover()
hybrid_remover = HybridTextRemover()

print("Testing text removal methods...\n")

# Edge-based
cleaned1, _ = edge_remover.remove_text(image.copy(), iterations=3)
cleaned1.save("outputs/final_edge_only.png")
print("[1] Edge-based: Good for small/distorted text")

# OCR-based
cleaned2, _ = remove_text_ocr(image.copy())
cleaned2.save("outputs/final_ocr_only.png")
print("[2] OCR-based: Good for large/clear text")

# Hybrid
cleaned3, _ = hybrid_remover.remove_text(image.copy(), iterations=2)
cleaned3.save("outputs/final_hybrid.png")
print("[3] Hybrid: Best of both worlds")

print("\n" + "="*60)
print("RESULTS:")
print("  final_edge_only.png - Edge detection (small text)")
print("  final_ocr_only.png - OCR detection (large text)")
print("  final_hybrid.png - HYBRID (large + small text)")
print("="*60)
print("\nHybrid should handle both large titles AND small text!")
