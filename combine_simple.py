#!/usr/bin/env python3
"""Simplified PosterO layout generation using POE API"""
import sys
import os
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET

def generate_simple_layout(image_path):
    """Generate simple 3-text layout without Part 1"""
    img = Image.open(image_path)
    w, h = img.size
    
    # Simple 3-region layout (title + 2 captions)
    regions = [
        (int(w*0.1), int(h*0.1), int(w*0.9), int(h*0.25)),  # Title (top)
        (int(w*0.1), int(h*0.7), int(w*0.5), int(h*0.85)),  # Caption 1
        (int(w*0.55), int(h*0.7), int(w*0.9), int(h*0.85)), # Caption 2
    ]
    
    # Generate SVG
    svg = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (x1, y1, x2, y2) in enumerate(regions, 1):
        svg += f'  <!-- Text {i} -->\n'
        svg += f'  <rect id="text_{i}" x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="none" stroke="green" stroke-width="2"/>\n'
    svg += '</svg>'
    
    return svg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combine_simple.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        svg_content = generate_simple_layout(image_path)
        
        # Save SVG
        with open("combined_output.svg", "w") as f:
            f.write(svg_content)
        
        # Save visualization
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Parse and draw boxes
        root = ET.fromstring(svg_content)
        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            x = int(rect.get('x'))
            y = int(rect.get('y'))
            w = int(rect.get('width'))
            h = int(rect.get('height'))
            draw.rectangle([x, y, x+w, y+h], outline='green', width=3)
        
        img.save("combined_visualization.png")
        print("✓ Layout saved to combined_output.svg")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
