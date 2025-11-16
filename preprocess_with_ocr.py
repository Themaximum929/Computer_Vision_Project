"""OCR-based text removal for LoRA preprocessing"""
import argparse
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from tqdm import tqdm

def remove_text_ocr(image):
    """Remove text using OCR detection + inpainting"""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=True)
    except:
        print("EasyOCR not available, using fallback method")
        return remove_text_fallback(image)
    
    img_array = np.array(image)
    
    # Detect text with OCR
    results = reader.readtext(img_array)
    
    if not results:
        return image, False
    
    # Create mask from detected text regions
    mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
    
    for (bbox, text, prob) in results:
        # Get bounding box coordinates
        pts = np.array(bbox, dtype=np.int32)
        
        # Expand bbox slightly to cover all text
        pts = pts * 1.1  # 10% expansion
        pts = pts.astype(np.int32)
        
        # Fill polygon
        cv2.fillPoly(mask, [pts], 255)
    
    # Dilate mask to ensure all text is covered
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Inpaint
    inpainted = cv2.inpaint(img_array, mask, 7, cv2.INPAINT_TELEA)
    
    return Image.fromarray(inpainted), True

def remove_text_fallback(image):
    """Fallback method without OCR"""
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Detect text-like regions
    # Method 1: MSER (Maximally Stable Extremal Regions)
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    
    mask = np.zeros(gray.shape, dtype=np.uint8)
    
    for region in regions:
        # Filter by size (text-like regions)
        if 50 < len(region) < 5000:
            hull = cv2.convexHull(region.reshape(-1, 1, 2))
            cv2.fillPoly(mask, [hull], 255)
    
    # Method 2: Stroke Width Transform approximation
    edges = cv2.Canny(gray, 50, 150)
    dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)
    
    # Combine masks
    combined_mask = cv2.bitwise_or(mask, dilated)
    
    # Filter small components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(combined_mask, connectivity=8)
    final_mask = np.zeros_like(combined_mask)
    
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if 100 < area < 50000:  # Text-sized regions
            final_mask[labels == i] = 255
    
    # Inpaint
    if final_mask.sum() > 0:
        inpainted = cv2.inpaint(img_array, final_mask, 7, cv2.INPAINT_TELEA)
        return Image.fromarray(inpainted), True
    
    return image, False

def preprocess_with_ocr(input_dir, output_dir, use_ocr=True):
    """Preprocess using OCR-based text detection"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    images = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    print(f"Found {len(images)} images")
    print(f"Method: {'OCR-based' if use_ocr else 'Fallback'}")
    
    stats = {'processed': 0, 'text_found': 0, 'no_text': 0}
    
    for img_file in tqdm(images, desc="Removing text"):
        try:
            image = Image.open(img_file).convert("RGB")
            
            if use_ocr:
                cleaned, text_found = remove_text_ocr(image)
            else:
                cleaned, text_found = remove_text_fallback(image)
            
            cleaned.save(output_path / img_file.name, quality=95)
            stats['processed'] += 1
            
            if text_found:
                stats['text_found'] += 1
            else:
                stats['no_text'] += 1
                
        except Exception as e:
            print(f"\nError {img_file.name}: {e}")
    
    # Copy metadata
    metadata = input_path / "metadata.json"
    if metadata.exists():
        import shutil
        shutil.copy(metadata, output_path / "metadata.json")
    
    print(f"\n{'='*60}")
    print(f"Processed: {stats['processed']}")
    print(f"Text removed: {stats['text_found']}")
    print(f"No text: {stats['no_text']}")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/posters")
    parser.add_argument("--output", default="data/posters_clean")
    parser.add_argument("--no-ocr", action="store_true", help="Use fallback without OCR")
    args = parser.parse_args()
    
    preprocess_with_ocr(args.input, args.output, not args.no_ocr)
