#!/usr/bin/env python3
"""
Generate poster layout for a single custom image using PosterO Part 1.

Usage:
    python generate_layout_single_image.py test.png output.svg
"""

import sys
import os
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add PosterO to path
sys.path.insert(0, 'PosterO/design_intent_detect')
sys.path.insert(0, 'PosterO')
from model import design_intent_detector

sys.path.insert(0, 'PosterO')
from llm_api_wrapper import LLM, SamplingParams
from layout_generate.layoutPlanter import LayoutPlanter


def detect_design_intent(image_path, model_path):
    """Detect available areas using design intent detection model."""
    # Load model
    model = design_intent_detector(act='none', action='forward')
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint)
    model.eval()
    
    # Load and preprocess image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((513, 750))  # PKU model training size
    
    # Convert to tensor and normalize
    img_tensor = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0)
    
    # Detect available areas (output is heatmap)
    with torch.no_grad():
        heatmap = model(img_tensor)
    
    # Convert heatmap to bounding boxes (threshold > 0.5)
    heatmap_np = heatmap[0, 0].cpu().numpy()
    threshold = 0.5
    binary_mask = (heatmap_np > threshold).astype(np.uint8)
    
    # Find contours to get bounding boxes
    from scipy import ndimage
    labeled, num_features = ndimage.label(binary_mask)
    bboxes = []
    min_area = 1000  # Minimum area in pixels (filter out tiny regions)
    
    for i in range(1, num_features + 1):
        mask = (labeled == i)
        coords = np.argwhere(mask)
        if len(coords) > 0:
            y1, x1 = coords.min(axis=0)
            y2, x2 = coords.max(axis=0)
            
            # Calculate area
            width = x2 - x1
            height = y2 - y1
            area = width * height
            
            # Filter out small regions
            if area < min_area:
                continue
            
            # Scale to canvas size
            x1 = int(x1 * 513 / heatmap_np.shape[1])
            x2 = int(x2 * 513 / heatmap_np.shape[1])
            y1 = int(y1 * 750 / heatmap_np.shape[0])
            y2 = int(y2 * 750 / heatmap_np.shape[0])
            bboxes.append((x1, y1, x2, y2))
    
    print(f"Filtered to {len(bboxes)} meaningful areas (removed small noise)")
    return bboxes, (513, 750)


def scale_svg_to_poster_size(svg_text, target_size=(720, 1280)):
    """Scale SVG from 513x750 to target poster size."""
    import re
    
    # Calculate scale factors
    scale_x = target_size[0] / 513
    scale_y = target_size[1] / 750
    
    # Update SVG canvas size
    svg_text = re.sub(r'<svg width="\d+"', f'<svg width="{target_size[0]}"', svg_text)
    svg_text = re.sub(r'height="\d+"', f'height="{target_size[1]}"', svg_text, count=1)
    
    # Scale all rect coordinates (handle both formats: with/without quotes)
    def scale_rect(match):
        elem_id = match.group(1)
        x_str = match.group(2).strip('"')
        y_str = match.group(3).strip('"')
        w_str = match.group(4).strip('"')
        h_str = match.group(5).strip('"')
        
        # Special case: don't scale canvas_0, just update its size
        if elem_id == 'canvas_0':
            return f'<rect id="{elem_id}" x="0" y="0" width="{target_size[0]}" height="{target_size[1]}"'
        
        x = int(float(x_str) * scale_x)
        y = int(float(y_str) * scale_y)
        w = int(float(w_str) * scale_x)
        h = int(float(h_str) * scale_y)
        return f'<rect id="{elem_id}" x="{x}" y="{y}" width="{w}" height="{h}"'
    
    svg_text = re.sub(
        r'<rect id="([^"]+)" x[=\s]*"?([^"\s>]+)"?\s*y[=\s]*"?([^"\s>]+)"?\s*width[=\s]*"?([^"\s>]+)"?\s*height[=\s]*"?([^"\s>]+)"?',
        scale_rect,
        svg_text
    )
    
    return svg_text


def visualize_layout(image_path, svg_text, available_areas, output_path):
    """Draw layout bounding boxes on the original image."""
    import re
    
    # Load and resize image (keep at 513x750 for visualization)
    img = Image.open(image_path).convert('RGB')
    img = img.resize((513, 750))
    draw = ImageDraw.Draw(img)
    
    # Draw available areas (yellow dashed)
    for x1, y1, x2, y2 in available_areas:
        for i in range(0, x2-x1, 10):
            draw.line([(x1+i, y1), (x1+i+5, y1)], fill='yellow', width=2)
            draw.line([(x1+i, y2), (x1+i+5, y2)], fill='yellow', width=2)
        for i in range(0, y2-y1, 10):
            draw.line([(x1, y1+i), (x1, y1+i+5)], fill='yellow', width=2)
            draw.line([(x2, y1+i), (x2, y1+i+5)], fill='yellow', width=2)
    
    # Parse SVG to extract element bounding boxes
    rect_pattern = re.compile(r'<rect id="([^"]+)" x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"')
    
    for match in rect_pattern.finditer(svg_text):
        elem_id = match.group(1)
        x = int(match.group(2))
        y = int(match.group(3))
        w = int(match.group(4))
        h = int(match.group(5))
        
        # Color by element type
        if 'text' in elem_id:
            color = 'green'
        elif 'logo' in elem_id:
            color = 'red'
        elif 'underlay' in elem_id:
            color = 'orange'
        else:
            color = 'blue'
        
        # Draw rectangle
        draw.rectangle([x, y, x+w, y+h], outline=color, width=3)
        
        # Draw label
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
        except:
            font = ImageFont.load_default()
        
        label = elem_id.split('_')[0]
        bbox = draw.textbbox((x, y-20), label, font=font)
        draw.rectangle(bbox, fill='white')
        draw.text((x, y-20), label, fill=color, font=font)
    
    img.save(output_path)


def generate_layout(available_areas, canvas_size):
    """Generate element layout using LLM based on available areas."""
    # Initialize LLM
    llm = LLM()
    sampl = SamplingParams(
        temperature=0.7,
        max_tokens=800,
        top_p=1.0,
        n=1,
        stop=["</svg>"]
    )
    
    # Create prompt with available areas
    areas_str = ", ".join([f"({x1}, {y1}, {x2}, {y2})" for x1, y1, x2, y2 in available_areas])
    
    prompt = f"""The following are some scalable vector graphics (svg) allocating elements on the canvas.

This svg uses canvas_0 of size {canvas_size} with available areas {areas_str} to allocate {{ text_1, text_2, underlay_1 }}.

Generate a valid SVG layout with elements placed within the available areas. Follow these rules:
1. Use only <rect> tags for elements
2. Elements MUST be within available areas - check that x+width <= area_x2 and y+height <= area_y2
3. Elements MUST be within canvas - check that x+width <= {canvas_size[0]} and y+height <= {canvas_size[1]}
4. Avoid overlapping elements
5. Use meaningful element IDs (text_1, text_2, logo_1, underlay_1, etc.)

Example format:
<svg width="{canvas_size[0]}" height="{canvas_size[1]}" xmlns="http://www.w3.org/2000/svg">
  <rect id="canvas_0" x="0" y="0" width="{canvas_size[0]}" height="{canvas_size[1]}" />
  <rect id="underlay_1" x="[x]" y="[y]" width="[w]" height="[h]" />
  <rect id="text_1" x="[x]" y="[y]" width="[w]" height="[h]" />
</svg>

Output the complete SVG:"""
    
    # Generate layout
    outputs = llm.generate(prompt, sampling_params=sampl)
    svg_text = outputs[0].outputs[0].text
    
    return svg_text


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_layout_single_image.py <image_path> [output.svg]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output_layout.svg"
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        print(f"Current directory: {os.getcwd()}")
        print("\nTry using full path, e.g.:")
        print("  python generate_layout_single_image.py src/test.png output.svg")
        sys.exit(1)
    
    print(f"Processing image: {image_path}")
    
    # Step 1: Detect design intent (available areas)
    model_path = "PosterO/design_intent_detect/pku_128_1e-06_none/ckpt/design_intent_pku_epoch100.pth"
    print(f"Loading design intent model from {model_path}...")
    
    available_areas, canvas_size = detect_design_intent(image_path, model_path)
    print(f"Detected {len(available_areas)} available areas: {available_areas}")
    
    # Step 2: Generate layout using LLM
    print("Generating layout with LLM...")
    svg_text = generate_layout(available_areas, canvas_size)
    
    # Step 3: Scale to poster size (720x1280)
    print("Scaling to poster size (720x1280)...")
    svg_text_scaled = scale_svg_to_poster_size(svg_text, target_size=(720, 1280))
    
    # Step 4: Save SVG
    with open(output_path, 'w') as f:
        f.write(svg_text_scaled)
    
    print(f"✓ Layout saved to {output_path}")
    
    # Step 5: Create visualization (use original 513x750 for visualization)
    viz_path = output_path.replace('.svg', '_visualization.png')
    visualize_layout(image_path, svg_text, available_areas, viz_path)
    print(f"✓ Visualization saved to {viz_path}")


if __name__ == "__main__":
    main()
