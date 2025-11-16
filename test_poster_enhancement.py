"""Test text removal + resolution enhancement on HuggingFace poster"""
import requests
from PIL import Image
from io import BytesIO
from src.aggressive_text_remover import AggressiveTextRemover
from src.super_resolution import SuperResolution
from pathlib import Path

# Download poster from HuggingFace
print("Downloading poster from HuggingFace...")
url = "https://datasets-server.huggingface.co/assets/stzhao/movie_posters_100k_controlnet/--/default/train/0/image/image.jpg"
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
except Exception as e:
    print(f"Failed to download from HuggingFace, using sample poster instead...")
    # Use a sample movie poster URL as fallback
    url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
    response = requests.get(url, timeout=30)
    image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
print(f"Original size: {image.size}")

# Save original
image.save("outputs/step1_original.png")
print("[OK] Step 1: Original saved")

# Test 1: Text removal only
print("\n--- Test 1: Text Removal Only ---")
remover = AggressiveTextRemover()
cleaned, text_found = remover.remove_text(image.copy(), iterations=3)
cleaned.save("outputs/step2_text_removed.png")
print(f"[OK] Step 2: Text removed (detected: {text_found})")

# Test 2: Resolution enhancement only
print("\n--- Test 2: Resolution Enhancement Only ---")
sr = SuperResolution()
enhanced = sr.enhance_details(image.copy())
enhanced.save("outputs/step3_resolution_enhanced.png")
print(f"[OK] Step 3: Resolution enhanced to {enhanced.size}")

# Test 3: Text removal THEN resolution enhancement
print("\n--- Test 3: Text Removal -> Resolution Enhancement ---")
cleaned2, _ = remover.remove_text(image.copy(), iterations=3)
final = sr.enhance_details(cleaned2)
final.save("outputs/step4_text_removed_then_enhanced.png")
print(f"[OK] Step 4: Combined (text removal first) - {final.size}")

# Test 4: Resolution enhancement THEN text removal
print("\n--- Test 4: Resolution Enhancement -> Text Removal ---")
enhanced2 = sr.enhance_details(image.copy())
final2, text_found2 = remover.remove_text(enhanced2, iterations=3)
final2.save("outputs/step5_enhanced_then_text_removed.png")
print(f"[OK] Step 5: Combined (enhancement first) - {final2.size}")
print(f"  Text detected on enhanced: {text_found2}")

print("\n" + "="*60)
print("RESULTS SAVED:")
print("  1. step1_original.png - Original poster")
print("  2. step2_text_removed.png - Text removal only")
print("  3. step3_resolution_enhanced.png - Resolution enhanced only")
print("  4. step4_text_removed_then_enhanced.png - Text removal -> Enhancement")
print("  5. step5_enhanced_then_text_removed.png - Enhancement -> Text removal")
print("="*60)
print("\nCompare to see which order works best!")
