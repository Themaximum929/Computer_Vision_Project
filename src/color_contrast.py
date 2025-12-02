"""Automatic Text Color Adjustment for Optimal Contrast"""
import colorsys
from PIL import Image

def get_average_color(image, bbox):
    """Get average color of a region in the image
    
    Args:
        image: PIL Image
        bbox: [x1, y1, x2, y2] bounding box
    
    Returns:
        (r, g, b) tuple
    """
    # Ensure valid bbox
    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return (128, 128, 128)  # Return gray for invalid bbox
    
    region = image.crop(bbox)
    pixels = list(region.getdata())
    
    if len(pixels) == 0:
        return (128, 128, 128)
    
    r_avg = sum(p[0] for p in pixels) // len(pixels)
    g_avg = sum(p[1] for p in pixels) // len(pixels)
    b_avg = sum(p[2] for p in pixels) // len(pixels)
    return (r_avg, g_avg, b_avg)

def rgb_to_hsv(rgb):
    """Convert RGB (0-255) to HSV (0-1)"""
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_rgb(hsv):
    """Convert HSV (0-1) to RGB (0-255)"""
    r, g, b = colorsys.hsv_to_rgb(*hsv)
    return tuple(int(x * 255) for x in (r, g, b))

def color_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors"""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def adjust_text_color(bg_color, text_color, threshold=100):
    """Adjust text color if too similar to background
    
    Args:
        bg_color: (r, g, b) background color
        text_color: (r, g, b) original text color
        threshold: minimum color distance (default 150)
    
    Returns:
        (r, g, b) adjusted text color
    """
    distance = color_distance(bg_color, text_color)
    print(f"    [Color Contrast] BG: {bg_color}, Text: {text_color}, Distance: {distance:.1f}")
    
    if distance >= threshold:
        print(f"    [Color Contrast] ✓ Sufficient contrast, keeping original color")
        return text_color
    
    # Convert to HSV for better color manipulation
    h, s, v = rgb_to_hsv(text_color)
    bg_h, bg_s, bg_v = rgb_to_hsv(bg_color)
    
    # If background is light, make text much darker
    if bg_v > 0.5:
        v = max(0.05, v - 0.7)
        s = min(1.0, s + 0.5)
        print(f"    [Color Contrast] Light BG detected (V={bg_v:.2f}), darkening text")
    else:
        # If background is dark, make text much lighter
        v = min(1.0, v + 0.7)
        s = min(1.0, s + 0.4)
        print(f"    [Color Contrast] Dark BG detected (V={bg_v:.2f}), lightening text")
    
    adjusted = hsv_to_rgb((h, s, v))
    print(f"    [Color Contrast] Adjusted: {text_color} → {adjusted}")
    return adjusted
