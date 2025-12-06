#!/usr/bin/env python3
"""Combine PosterO Part 1 (Design Intent) + Part 2 (LLM Layout)"""
import sys
import os
import subprocess
from pathlib import Path

def run_part1(image_path):
    """Run design intent detection"""
    cmd = [
        "python", "PosterO/design_intent_detect/main.py",
        "--image_path", image_path,
        "--output_dir", "."
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Part 1 failed: {result.stderr}")
    return "design_intent_output.json"

def run_part2(image_path, design_intent_path):
    """Run LLM layout generation"""
    cmd = [
        "python", "PosterO/main_api.py",
        "--image_path", image_path,
        "--design_intent", design_intent_path,
        "--output_svg", "combined_output.svg"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Part 2 failed: {result.stderr}")
    return "combined_output.svg"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combine_simple.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        # Part 1: Design Intent Detection
        design_intent = run_part1(image_path)
        
        # Part 2: LLM Layout Generation
        svg_output = run_part2(image_path, design_intent)
        
        print(f"✓ Layout saved to {svg_output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
