"""Test if ACTUAL upscaling improves text removal"""
import requests
from PIL import Image
from io import BytesIO
from src.aggressive_text_remover import AggressiveTextRemover
from src.super_resolution import SuperResolution
from pathlib import Path

url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
response = requests.get(url, timeout=30)
image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
remover = AggressiveTextRemover()
sr = SuperResolution()

print(f"Original: {image.size}")

# Method 1: Direct text removal
cleaned1, _ = remover.remove_text(image.copy(), iterations=3)
cleaned1.save("outputs/method1_direct_removal.png")
print("[1] Direct removal")

# Method 2: Upscale 2x -> Remove text -> Downscale
upscaled = sr.upscale(image.copy(), scale=2.0)
print(f"Upscaled: {upscaled.size}")
cleaned2, _ = remover.remove_text(upscaled, iterations=3)
downscaled = cleaned2.resize(image.size, Image.LANCZOS)
downscaled.save("outputs/method2_upscale_remove_downscale.png")
print("[2] Upscale -> Remove -> Downscale")

print("\nCompare method1 vs method2 to see if upscaling helps!")
