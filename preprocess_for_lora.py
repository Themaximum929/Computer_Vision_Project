"""Enhanced preprocessing for LoRA training - AI-based inpainting"""
import argparse
from pathlib import Path
from PIL import Image, ImageFilter
import cv2
import numpy as np
from tqdm import tqdm

class SmartTextRemover:
    """Smart text removal with inpainting to avoid blank areas"""
    
    def remove_text_with_inpainting(self, image):
        """Remove text and fill with content-aware inpainting"""
        img_array = np.array(image)
        
        # Detect text regions
        mask = self._detect_text_mask(img_array)
        
        # If no text detected, return original
        if mask.sum() == 0:
            return image, False
        
        # Inpaint text regions
        inpainted = cv2.inpaint(img_array, mask, 7, cv2.INPAINT_TELEA)
        
        return Image.fromarray(inpainted), True
    
    def _detect_text_mask(self, img_array):
        """Detect text regions and create mask"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Method 1: Edge detection for text
        edges = cv2.Canny(gray, 50, 150)
        
        # Method 2: Adaptive threshold for text
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Combine masks
        combined = cv2.bitwise_or(edges, thresh)
        
        # Morphological operations to connect text regions
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(combined, kernel, iterations=2)
        
        # Filter small regions (noise)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Only keep text-sized regions (not too small, not too large)
            if 50 < area < 50000:
                cv2.drawContours(mask, [contour], -1, 255, -1)
        
        return mask.astype(np.uint8)

def preprocess_for_lora(input_dir, output_dir, quality_check=True):
    """Preprocess posters for LoRA training with quality checks"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create rejected folder for manual review
    rejected_path = output_path / "rejected"
    rejected_path.mkdir(exist_ok=True)
    
    image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return
    
    print(f"Found {len(image_files)} images")
    print("Using smart text removal with inpainting")
    
    remover = SmartTextRemover()
    stats = {'processed': 0, 'rejected': 0, 'no_text': 0}
    
    for img_file in tqdm(image_files, desc="Processing"):
        try:
            image = Image.open(img_file).convert("RGB")
            
            # Remove text with inpainting
            cleaned, text_found = remover.remove_text_with_inpainting(image)
            
            if quality_check:
                # Check if result is too blank
                img_array = np.array(cleaned)
                brightness = img_array.mean()
                variance = img_array.std()
                
                # Reject if too uniform (likely blank)
                if variance < 20 or brightness < 30 or brightness > 225:
                    cleaned.save(rejected_path / img_file.name)
                    stats['rejected'] += 1
                    continue
            
            # Save cleaned image
            cleaned.save(output_path / img_file.name, quality=95)
            stats['processed'] += 1
            
            if not text_found:
                stats['no_text'] += 1
                
        except Exception as e:
            print(f"\nError: {img_file.name}: {e}")
            stats['rejected'] += 1
    
    # Copy metadata
    metadata_file = input_path / "metadata.json"
    if metadata_file.exists():
        import shutil
        shutil.copy(metadata_file, output_path / "metadata.json")
    
    print(f"\n{'='*60}")
    print(f"PREPROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Processed: {stats['processed']}")
    print(f"Rejected (blank/low quality): {stats['rejected']}")
    print(f"No text detected: {stats['no_text']}")
    print(f"\nOutput: {output_path}")
    print(f"Rejected: {rejected_path} (review manually)")
    print(f"\nNext: Review rejected images and move good ones to output")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/posters", help="Input directory")
    parser.add_argument("--output", default="data/posters_lora", help="Output directory")
    parser.add_argument("--no-quality-check", action="store_true", help="Skip quality checks")
    args = parser.parse_args()
    
    preprocess_for_lora(args.input, args.output, not args.no_quality_check)
