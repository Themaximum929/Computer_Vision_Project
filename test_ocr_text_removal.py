"""Compare edge-based vs OCR-based text removal with resolution enhancement"""
import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
from pathlib import Path

try:
    import pytesseract
    HAS_OCR = True
except:
    HAS_OCR = False
    print("WARNING: pytesseract not installed, OCR test will be skipped")

from src.aggressive_text_remover import AggressiveTextRemover
from src.super_resolution import SuperResolution

def ocr_text_removal(image, upscale=False):
    """Remove text using OCR detection"""
    if not HAS_OCR:
        return image, False
    
    img_array = np.array(image)
    
    # Upscale if requested
    if upscale:
        h, w = img_array.shape[:2]
        img_array = cv2.resize(img_array, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
    
    # OCR detection
    data = pytesseract.image_to_data(img_array, output_type=pytesseract.Output.DICT)
    mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
    
    text_found = False
    for i, conf in enumerate(data['conf']):
        if int(conf) > 30:  # Confidence threshold
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            cv2.rectangle(mask, (x-10, y-10), (x+w+10, y+h+10), 255, -1)
            text_found = True
    
    # Inpaint
    if text_found:
        img_array = cv2.inpaint(img_array, mask, 20, cv2.INPAINT_TELEA)
    
    # Downscale if upscaled
    if upscale:
        img_array = cv2.resize(img_array, (w, h), interpolation=cv2.INTER_LANCZOS4)
    
    return Image.fromarray(img_array), text_found

# Download poster
url = "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
response = requests.get(url, timeout=30)
image = Image.open(BytesIO(response.content))

Path("outputs").mkdir(exist_ok=True)
image.save("outputs/original.png")
print(f"Original: {image.size}")

remover = AggressiveTextRemover()
sr = SuperResolution()

# Test 1: Edge-based (current method)
cleaned1, found1 = remover.remove_text(image.copy(), iterations=3)
cleaned1.save("outputs/test1_edge_based.png")
print(f"[1] Edge-based: Text found={found1}")

# Test 2: Edge-based with enhancement
enhanced = sr.enhance_details(image.copy())
cleaned2, found2 = remover.remove_text(enhanced, iterations=3)
cleaned2.save("outputs/test2_edge_enhanced.png")
print(f"[2] Edge + Enhancement: Text found={found2}")

# Test 3: OCR-based
if HAS_OCR:
    cleaned3, found3 = ocr_text_removal(image.copy(), upscale=False)
    cleaned3.save("outputs/test3_ocr_based.png")
    print(f"[3] OCR-based: Text found={found3}")
    
    # Test 4: OCR with upscaling
    cleaned4, found4 = ocr_text_removal(image.copy(), upscale=True)
    cleaned4.save("outputs/test4_ocr_upscaled.png")
    print(f"[4] OCR + Upscale: Text found={found4}")
else:
    print("[3] OCR-based: SKIPPED (install pytesseract)")
    print("[4] OCR + Upscale: SKIPPED (install pytesseract)")

print("\nCompare outputs to see which method works best!")
