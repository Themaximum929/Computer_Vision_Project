#!/usr/bin/env python3
"""
Add title and captions to poster using PosterO text element bboxes
"""

import re
import random
import glob
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageStat

def extract_text_bboxes(svg_content):
    """Extract text element bounding boxes from SVG."""
    svg_clean = svg_content.replace('```svg', '').replace('```', '').strip()
    
    # Pattern 1: Match comments like <!-- Text 1 --> or <!-- text_1: --> followed by <rect>
    comment_pattern = re.compile(
        r'<!--\s*[Tt]ext[_ ]?(\d+)[^>]*?-->\s*'
        r'<rect[^>]*?x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?width="([^"]+)"[^>]*?height="([^"]+)"',
        re.DOTALL | re.IGNORECASE
    )
    
    # Pattern 2: Match <rect id="text_N" ...>
    id_pattern = re.compile(
        r'<rect[^>]*?id="(text_\d+)"[^>]*?'
        r'x="([^"]+)"[^>]*?y="([^"]+)"[^>]*?'
        r'width="([^"]+)"[^>]*?height="([^"]+)"',
        re.DOTALL
    )
    
    text_boxes = []
    
    # Try comment pattern first
    for match in comment_pattern.finditer(svg_clean):
        elem_id = match.group(1)
        x = int(float(match.group(2)))
        y = int(float(match.group(3)))
        w = int(float(match.group(4)))
        h = int(float(match.group(5)))
        text_boxes.append({'id': elem_id, 'bbox': (x, y, x+w, y+h)})
    
    # Try id pattern if no results
    if not text_boxes:
        for match in id_pattern.finditer(svg_clean):
            elem_id = match.group(1)
            x = int(float(match.group(2)))
            y = int(float(match.group(3)))
            w = int(float(match.group(4)))
            h = int(float(match.group(5)))
            text_boxes.append({'id': elem_id, 'bbox': (x, y, x+w, y+h)})
    
    # Sort by area (largest first for title, smaller for captions)
    text_boxes.sort(key=lambda b: (b['bbox'][2]-b['bbox'][0])*(b['bbox'][3]-b['bbox'][1]), reverse=True)
    
    return text_boxes


def fit_text_to_bbox(text, bbox, draw, font_path, max_font_size=120, min_font_size=20, use_shared_font=True):
    """Find optimal font size to fit text in bbox."""
    x1, y1, x2, y2 = bbox
    box_w, box_h = x2 - x1, y2 - y1
    
    # Dynamic max font size based on box height
    dynamic_max = min(int(box_h * 0.6), max_font_size)
    dynamic_min = max(int(box_h * 0.15), min_font_size)
    
    for size in range(dynamic_max, dynamic_min - 1, -2):
        try:
            # Use the provided font_path (already selected once per poster)
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.load_default()
            return font, text
        
        # Get text dimensions
        bbox_text = draw.textbbox((0, 0), text, font=font)
        text_w = bbox_text[2] - bbox_text[0]
        text_h = bbox_text[3] - bbox_text[1]
        
        # Check if fits with padding
        if text_w <= box_w * 0.95 and text_h <= box_h * 0.85:
            return font, text
    
    # If still doesn't fit, try wrapping
    font = ImageFont.truetype(font_path, dynamic_min)
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox_text = draw.textbbox((0, 0), test_line, font=font)
        if bbox_text[2] - bbox_text[0] <= box_w * 0.95:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return font, '\n'.join(lines)


def get_contrasting_color(image, bbox):
    """Get contrasting and varied text color based on background."""
    x1, y1, x2, y2 = bbox
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(image.width, x2), min(image.height, y2)
    
    if x2 <= x1 or y2 <= y1:
        return (255, 255, 255)
    
    region = image.crop((x1, y1, x2, y2))
    stat = ImageStat.Stat(region)
    avg_brightness = sum(stat.mean) / 3
    
    # Get dominant color
    avg_r, avg_g, avg_b = stat.mean[:3]
    
    # Generate varied colors with good contrast
    if avg_brightness < 100:  # Very dark background
        # Bright varied colors
        colors = [(255, 255, 255), (255, 220, 100), (100, 200, 255), (255, 150, 150)]
    elif avg_brightness < 160:  # Medium background
        # High contrast colors
        colors = [(255, 255, 255), (255, 200, 50), (50, 255, 200), (255, 100, 100)]
    else:  # Light background
        # Dark varied colors
        colors = [(20, 20, 20), (80, 40, 120), (120, 40, 40), (40, 80, 120)]
    
    return random.choice(colors)


def select_font_for_style(prompt):
    """Randomly select font from fonts folder."""
    font_files = glob.glob("fonts/*.ttf") + glob.glob("fonts/*.otf")
    if not font_files:
        return "fonts/Graduate-Regular.ttf"
    return random.choice(font_files)


def add_text_to_poster(image_path, svg_path, title, captions, output_path, font_path=None, style_prompt="", shared_font=None):
    """
    Add title and captions to poster using PosterO text bboxes.
    
    Args:
        image_path: Path to base poster image
        svg_path: Path to PosterO SVG layout
        title: Main title text
        captions: List of caption strings
        output_path: Where to save final poster
        font_path: Path to font file
    """
    # Use shared font if provided, otherwise select one
    if shared_font:
        font_path = shared_font
    elif font_path is None:
        font_path = select_font_for_style(style_prompt)
    
    # Load image and upscale to final resolution first
    img = Image.open(image_path).convert('RGBA')
    original_size = img.size
    target_size = (720, 1280)
    scale_x = target_size[0] / original_size[0]
    scale_y = target_size[1] / original_size[1]
    img = img.resize(target_size, Image.LANCZOS)
    
    with open(svg_path, 'r') as f:
        svg_content = f.read()
    
    # Extract text bboxes
    text_boxes = extract_text_bboxes(svg_content)
    
    if not text_boxes:
        print("⚠ No text boxes found in layout")
        img = img.convert('RGB')
        img.save(output_path)
        return
    
    # Scale text boxes to final resolution
    text_boxes = [{
        'id': box['id'],
        'bbox': (
            int(box['bbox'][0] * scale_x),
            int(box['bbox'][1] * scale_y),
            int(box['bbox'][2] * scale_x),
            int(box['bbox'][3] * scale_y)
        )
    } for box in text_boxes]
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Add title to largest text box
    if title and len(text_boxes) > 0:
        title_box = text_boxes[0]['bbox']
        font, fitted_text = fit_text_to_bbox(title, title_box, draw, font_path, max_font_size=120)
        
        # Get contrasting color
        text_color = get_contrasting_color(img, title_box)
        outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
        
        # Center text in bbox
        x1, y1, x2, y2 = title_box
        bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
        text_w = bbox_text[2] - bbox_text[0]
        text_h = bbox_text[3] - bbox_text[1]
        
        text_x = x1 + (x2 - x1 - text_w) // 2
        text_y = y1 + (y2 - y1 - text_h) // 2
        
        # Draw with smooth outline (stroke method for better quality)
        # Multiple passes for thick outline
        outline_width = max(2, int(font.size / 20))
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
        draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
        
        print(f"✓ Added title: '{title}' (color: {text_color})")
    
    # Add captions to remaining text boxes
    for i, caption in enumerate(captions):
        if i + 1 >= len(text_boxes):
            break
        
        caption_box = text_boxes[i + 1]['bbox']
        font, fitted_text = fit_text_to_bbox(caption, caption_box, draw, font_path, max_font_size=60)
        
        # Get contrasting color
        text_color = get_contrasting_color(img, caption_box)
        outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
        
        # Center text
        x1, y1, x2, y2 = caption_box
        bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
        text_w = bbox_text[2] - bbox_text[0]
        text_h = bbox_text[3] - bbox_text[1]
        
        text_x = x1 + (x2 - x1 - text_w) // 2
        text_y = y1 + (y2 - y1 - text_h) // 2
        
        # Draw with smooth outline
        outline_width = max(2, int(font.size / 25))
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
        draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
        
        print(f"✓ Added caption {i+1}: '{caption}' (color: {text_color})")
    
    # Save (already at 720x1280)
    img = img.convert('RGB')
    img.save(output_path)
    print(f"✓ Saved final poster to {output_path} (720x1280)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python add_text_to_poster.py <image> <svg> <title> <caption1> [caption2] ...")
        sys.exit(1)
    
    image_path = sys.argv[1]
    svg_path = sys.argv[2]
    title = sys.argv[3]
    captions = sys.argv[4:]
    
    output_path = image_path.replace('.png', '_with_text.png')
    
    add_text_to_poster(image_path, svg_path, title, captions, output_path)
