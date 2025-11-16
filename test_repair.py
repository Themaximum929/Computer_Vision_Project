"""Test hybrid text removal with repair mechanism"""
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from src.hybrid_text_remover import HybridTextRemover

url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
response = requests.get(url, timeout=30)
image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
remover = HybridTextRemover()

print("Testing repair mechanism...\n")

# Without repair
cleaned1, _ = remover.remove_text(image.copy(), iterations=2, repair=False)
cleaned1.save("outputs/repair_without.png")
print("[1] Without repair - may have distortions")

# With repair
cleaned2, _ = remover.remove_text(image.copy(), iterations=2, repair=True)
cleaned2.save("outputs/repair_with.png")
print("[2] With repair - smoothed distortions")

print("\n" + "="*60)
print("Compare:")
print("  repair_without.png - Text removed but distorted")
print("  repair_with.png - Text removed + repaired (SMOOTH)")
print("="*60)
