"""Compare pixel differences between images"""
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

# Load images
img1 = Image.open("outputs/step2_text_removed.png")
img2 = Image.open("outputs/step5_enhanced_then_text_removed.png")

# Calculate difference
diff = ImageChops.difference(img1, img2)

# Enhance difference for visibility
enhancer = ImageEnhance.Brightness(diff)
diff_enhanced = enhancer.enhance(10.0)

# Save
diff_enhanced.save("outputs/difference_map.png")

# Calculate statistics
diff_array = np.array(diff)
total_pixels = diff_array.size
changed_pixels = np.count_nonzero(diff_array)
percent_changed = (changed_pixels / total_pixels) * 100

print(f"Pixel difference: {percent_changed:.4f}%")
print(f"Changed pixels: {changed_pixels:,} / {total_pixels:,}")
print(f"Max difference: {diff_array.max()}")
print(f"Mean difference: {diff_array.mean():.2f}")

if percent_changed < 0.01:
    print("\nCONCLUSION: Images are virtually identical")
    print("Super-resolution enhancement does NOT improve text removal")
else:
    print(f"\nDifference map saved: outputs/difference_map.png")
