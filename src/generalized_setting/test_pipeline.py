"""
Test script for the layout generation pipeline.
Tests the pipeline with test.png image.

Usage:
    # Basic test with default settings
    python test_pipeline.py
    
    # Test with specific image
    python test_pipeline.py --image /path/to/image.png
    
    # Test with different dataset category
    python test_pipeline.py --dataset movie-poster
    
    # Simple test (just check imports)
    python test_pipeline.py --simple

Requirements:
    - test.png in project root (or specify with --image)
    - Dataset directories properly configured
    - LLM API key set (POE_API_KEY environment variable)
    - Preprocessed dataset files (.pt files) available
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse, PathPatch
from matplotlib.path import Path as MPLPath

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import LayoutGenerationPipeline


def get_image_size(image_path: str) -> tuple:
    """Get image dimensions."""
    img = Image.open(image_path)
    return img.size  # (width, height)


def create_example_bboxes(image_size: tuple, num_bboxes: int = 3) -> list:
    """
    Create example design intent bounding boxes.
    In a real scenario, these would come from a design intent detection model.
    
    Args:
        image_size: (width, height) of the image
        num_bboxes: Number of bounding boxes to generate
    
    Returns:
        List of bounding boxes in format [(x1, y1, x2, y2), ...]
    """
    width, height = image_size
    
    # Create some example bounding boxes covering different regions
    # These are just examples - in practice, use actual design intent detection
    bboxes = []
    
    if num_bboxes >= 1:
        # Top region (for title/header)
        bboxes.append((int(width * 0.1), int(height * 0.05), 
                       int(width * 0.9), int(height * 0.25)))
    
    if num_bboxes >= 2:
        # Middle region (for main content)
        bboxes.append((int(width * 0.1), int(height * 0.3), 
                       int(width * 0.9), int(height * 0.7)))
    
    if num_bboxes >= 3:
        # Bottom region (for footer/logo)
        bboxes.append((int(width * 0.2), int(height * 0.75), 
                       int(width * 0.8), int(height * 0.95)))
    
    return bboxes


def parse_svg_elements(svg_string: str):
    """
    Parse SVG string to extract elements (rects, ellipses, paths).
    
    Returns:
        List of dictionaries with element information
    """
    elements = []
    
    # Extract SVG canvas size
    svg_size_match = re.search(r'<svg.*?width="(\d+)".*?height="(\d+)"', svg_string)
    if svg_size_match:
        svg_width = int(svg_size_match.group(1))
        svg_height = int(svg_size_match.group(2))
    else:
        svg_width = svg_height = None
    
    # Parse rectangles
    rect_pattern = re.compile(r'<rect id="([^"]+)" x=([^\s>]+) y=([^\s>]+) width=([^\s>]+) height=([^\s>]+)[^>]*/?>')
    for match in rect_pattern.finditer(svg_string):
        elem_id = match.group(1)
        x = float(match.group(2).replace('"', ''))
        y = float(match.group(3).replace('"', ''))
        w = float(match.group(4).replace('"', ''))
        h = float(match.group(5).replace('"', ''))
        
        # Check for rotation
        rotation = None
        transform_match = re.search(r'transform="rotate\(([^)]+)\)"', match.group(0))
        if transform_match:
            rotation = float(transform_match.group(1).split()[0])
        
        elements.append({
            'type': 'rect',
            'id': elem_id,
            'x': x, 'y': y, 'width': w, 'height': h,
            'rotation': rotation
        })
    
    # Parse ellipses
    ellipse_pattern = re.compile(r'<ellipse id="([^"]+)" cx=([^\s>]+) cy=([^\s>]+) rx=([^\s>]+) ry=([^\s>]+)[^>]*/?>')
    for match in ellipse_pattern.finditer(svg_string):
        elem_id = match.group(1)
        cx = float(match.group(2).replace('"', ''))
        cy = float(match.group(3).replace('"', ''))
        rx = float(match.group(4).replace('"', ''))
        ry = float(match.group(5).replace('"', ''))
        
        elements.append({
            'type': 'ellipse',
            'id': elem_id,
            'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry
        })
    
    # Parse paths (simplified - just extract the path data)
    path_pattern = re.compile(r'<path id="([^"]+)" d="([^"]+)"[^>]*/?>')
    for match in path_pattern.finditer(svg_string):
        elem_id = match.group(1)
        path_data = match.group(2)
        
        elements.append({
            'type': 'path',
            'id': elem_id,
            'd': path_data
        })
    
    return elements, (svg_width, svg_height)


def get_element_color(elem_id: str, label_info: dict) -> str:
    """Get color for an element based on its ID and label_info."""
    # Extract label type from ID (e.g., "text-general_1" -> "text-general")
    label_type = None
    for label, info in label_info.items():
        if info['type'] in elem_id:
            return info.get('color', 'blue')
    
    # Default colors based on element type
    if 'text' in elem_id.lower():
        return 'green'
    elif 'logo' in elem_id.lower():
        return 'red'
    elif 'underlay' in elem_id.lower():
        return 'orange'
    elif 'embellishment' in elem_id.lower():
        return 'blue'
    elif 'canvas' in elem_id.lower():
        return 'gray'
    else:
        return 'purple'


def visualize_layout_on_image(
    image_path: str,
    svg_string: str,
    layout_graph: dict,
    label_info: dict,
    canvas_size: tuple,
    output_path: str = None,
    show_design_intent: list = None
):
    """
    Draw the generated SVG layout on top of the test image.
    
    Args:
        image_path: Path to the original image
        svg_string: Generated SVG string
        layout_graph: Layout graph dictionary with cls_elem and box_elem
        label_info: Label information dictionary
        canvas_size: Canvas size used (width, height)
        output_path: Path to save the visualization (default: image_path with _layout suffix)
        show_design_intent: Optional list of design intent bounding boxes to show
    """
    # Load image
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    # Parse SVG elements
    svg_elements, svg_size = parse_svg_elements(svg_string)
    
    # Calculate scaling factor if canvas size differs from image size
    if svg_size[0] and svg_size[1]:
        scale_x = img_width / svg_size[0]
        scale_y = img_height / svg_size[1]
    else:
        scale_x = img_width / canvas_size[0]
        scale_y = img_height / canvas_size[1]
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(img_width/100, img_height/100), dpi=100)
    ax.imshow(img, origin='upper')  # Use upper origin for image coordinates
    ax.set_xlim(0, img_width)
    ax.set_ylim(img_height, 0)  # Set y-axis limits (top to bottom)
    ax.axis('off')
    
    # Draw design intent bounding boxes (if provided)
    if show_design_intent:
        for bbox in show_design_intent:
            x1, y1, x2, y2 = bbox
            # Scale if needed
            if canvas_size != (img_width, img_height):
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
            
            rect = Rectangle(
                (x1, y1), x2 - x1, y2 - y1,
                linewidth=2, edgecolor='yellow', facecolor='none',
                linestyle='--', alpha=0.7, label='Design Intent'
            )
            ax.add_patch(rect)
    
    # Draw SVG elements
    for i, elem in enumerate(svg_elements):
        if elem['type'] == 'rect':
            x = elem['x'] * scale_x
            y = elem['y'] * scale_y
            w = elem['width'] * scale_x
            h = elem['height'] * scale_y
            
            color = get_element_color(elem['id'], label_info)
            
            # Skip canvas element
            if 'canvas' in elem['id'].lower():
                continue
            
            rect = Rectangle(
                (x, y), w, h,
                linewidth=2, edgecolor=color, facecolor='none',
                alpha=0.8
            )
            ax.add_patch(rect)
            
            # Add label
            ax.text(x + w/2, y + h/2, elem['id'].split('_')[0],
                   ha='center', va='center', fontsize=8, color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        elif elem['type'] == 'ellipse':
            cx = elem['cx'] * scale_x
            cy = elem['cy'] * scale_y
            rx = elem['rx'] * scale_x
            ry = elem['ry'] * scale_y
            
            color = get_element_color(elem['id'], label_info)
            
            ellipse = Ellipse(
                (cx, cy), rx * 2, ry * 2,
                linewidth=2, edgecolor=color, facecolor='none',
                alpha=0.8
            )
            ax.add_patch(ellipse)
            
            # Add label
            ax.text(cx, cy, elem['id'].split('_')[0],
                   ha='center', va='center', fontsize=8, color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        elif elem['type'] == 'path':
            # For paths, we'll just draw a bounding box approximation
            # In a full implementation, you'd parse the path data properly
            color = get_element_color(elem['id'], label_info)
            ax.text(img_width * 0.5, img_height * 0.1 + i * 20, 
                   f"{elem['id']}: path (complex)",
                   fontsize=8, color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Also draw from layout_graph if available (more accurate)
    if layout_graph and 'box_elem' in layout_graph:
        for i, (cls, box) in enumerate(zip(layout_graph.get('cls_elem', []), layout_graph['box_elem'])):
            if isinstance(box, str):  # Path data
                continue
            
            if len(box) >= 4:
                # Handle different box formats
                if len(box) == 4:  # [x, y, x2, y2] or [x, y, w, h]
                    x1, y1, x2, y2 = box[:4]
                    # Check if it's width/height or coordinates
                    if x2 < x1 or y2 < y1:
                        # It's width/height format
                        x, y, w, h = box
                        x2 = x + w
                        y2 = y + h
                    else:
                        x, y = x1, y1
                        w = x2 - x1
                        h = y2 - y1
                else:
                    continue
                
                # Scale if needed
                if canvas_size != (img_width, img_height):
                    x = int(x * scale_x)
                    y = int(y * scale_y)
                    w = int(w * scale_x)
                    h = int(h * scale_y)
                
                # Get color from label_info
                color = 'blue'
                if isinstance(cls, str):
                    for label, info in label_info.items():
                        if info['type'] in cls or cls in info['type']:
                            color = info.get('color', 'blue')
                            break
                elif cls in label_info:
                    color = label_info[cls].get('color', 'blue')
                
                # Draw rectangle
                rect = Rectangle(
                    (x, y), w, h,
                    linewidth=2, edgecolor=color, facecolor='none',
                    alpha=0.6, linestyle=':'
                )
                ax.add_patch(rect)
    
    # Add legend
    if show_design_intent:
        ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    
    # Save figure
    if output_path is None:
        output_path = str(Path(image_path).with_suffix('')) + '_layout.png'
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0)
    print(f"\n✓ Visualization saved to: {output_path}")
    
    # Close the figure to free memory
    plt.close(fig)
    
    return output_path


def load_design_intent_bboxes_from_file(bbox_dir: str, image_name: str) -> list:
    """
    Try to load design intent bounding boxes from preprocessed files.
    This is a helper function - in practice, you'd use a design intent detection model.
    """
    import torch
    
    # Try to load from test split
    test_file = os.path.join(bbox_dir, "design_intent_bbox_test.pt")
    if os.path.exists(test_file):
        try:
            db_test = torch.load(test_file, weights_only=False)
            # Try to find matching image
            for entry in db_test:
                if image_name in entry.get('poster_path', ''):
                    return entry.get('den_box', [])
        except Exception as e:
            print(f"  Could not load from {test_file}: {e}")
    
    return None


def test_pipeline_basic(image_path: str = None, dataset_category: str = 'movie-poster', no_vis: bool = False):
    """Test basic pipeline functionality."""
    print("=" * 80)
    print("Testing Layout Generation Pipeline")
    print("=" * 80)
    
    # Get the test image path
    if image_path is None:
        script_dir = Path(__file__).parent.parent
        test_image_path = script_dir / "test.png"
    else:
        test_image_path = Path(image_path)
    
    if not test_image_path.exists():
        print(f"ERROR: Test image not found at {test_image_path}")
        print("Please ensure the image exists or specify the path with --image")
        return False
    
    print(f"\n✓ Found test image: {test_image_path}")
    
    # Get image size
    img_size = get_image_size(str(test_image_path))
    print(f"✓ Image size: {img_size[0]}x{img_size[1]}")
    
    # Setup dataset info - using specified category
    # You may need to adjust these paths based on your setup
    script_dir = Path(__file__).parent.parent
    base_dir = script_dir
    dataset_info = {
        'dataset_name': f'pstylish7_{dataset_category}',
        'design_intent_bbox_dir': str(base_dir / 'Dataset' / 'PStylish7' / dataset_category / 'predm_zs'),
        'annotation_dir': str(base_dir / 'Dataset' / 'PStylish7' / dataset_category),
        'label_info': {
            'T-G': {'type': 'text-general', 'color': 'green'},
            'T-V': {'type': 'text-vertical', 'color': 'green'},
            'T-R': {'type': 'text-rotated', 'color': 'green'},
            'T-S': {'type': 'text-ellipse', 'color': 'green'},
            'T-C': {'type': 'text-curved', 'color': 'green'},
            'L': {'type': 'logo', 'color': 'red'},
            'U': {'type': 'underlay', 'color': 'orange'},
            'E': {'type': 'embellishment', 'color': 'blue'}
        }
    }
    
    print(f"\n✓ Dataset: {dataset_info['dataset_name']}")
    print(f"✓ Design intent bbox dir: {dataset_info['design_intent_bbox_dir']}")
    print(f"✓ Annotation dir: {dataset_info['annotation_dir']}")
    
    # Check if directories exist
    if not os.path.exists(dataset_info['design_intent_bbox_dir']):
        print(f"\n⚠ WARNING: Design intent bbox directory not found!")
        print(f"  Expected: {dataset_info['design_intent_bbox_dir']}")
        print(f"  The pipeline may fail if this directory doesn't exist.")
        print(f"  Please adjust the path in the test script if needed.\n")
    
    # Try to load design intent bboxes from file, otherwise create examples
    design_intent_bboxes = None
    if os.path.exists(dataset_info['design_intent_bbox_dir']):
        print("\n  Attempting to load design intent bboxes from preprocessed files...")
        design_intent_bboxes = load_design_intent_bboxes_from_file(
            dataset_info['design_intent_bbox_dir'],
            'test.png'
        )
    
    if design_intent_bboxes is None:
        print("  No preprocessed bboxes found. Creating example bboxes...")
        design_intent_bboxes = create_example_bboxes(img_size, num_bboxes=3)
    else:
        print(f"  ✓ Loaded {len(design_intent_bboxes)} design intent bboxes from file")
    
    print(f"\n✓ Using {len(design_intent_bboxes)} design intent bounding boxes:")
    for i, bbox in enumerate(design_intent_bboxes):
        print(f"  Box {i+1}: ({bbox[0]}, {bbox[1]}) -> ({bbox[2]}, {bbox[3]})")
    
    try:
        print("\n" + "=" * 80)
        print("Initializing Pipeline...")
        print("=" * 80)
        
        # Initialize pipeline with minimal settings for testing
        pipeline = LayoutGenerationPipeline(
            dataset_info=dataset_info,
            strategy={'structure': 'plain', 'injection': 'top'},
            canvas_size=(513, 750),
            pool_strategy='all',  # Use all samples for simplicity
            rank_strategy='random',  # Random ranking for speed
            sample_size=3,  # Use fewer samples for faster testing
            llm_params={
                'temperature': 0.7,
                'max_tokens': 800,
                'num_return': 5,  # Generate 5 candidates
            },
            seed=42
        )
        
        print("✓ Pipeline initialized successfully")
        
        print("\n" + "=" * 80)
        print("Generating Layout...")
        print("=" * 80)
        print("This may take a while as it calls the LLM API...")
        
        # Generate layout
        result = pipeline.generate_layout(
            image=str(test_image_path),
            design_intent_bboxes=design_intent_bboxes,
            num_generations=1,  # Generate 1 layout for testing
            label_rback=False,
            labels= ['T-G', 'T-V', 'T-R', 'T-S', 'T-C', 'L', 'U', 'E']
        )
        
        print("\n" + "=" * 80)
        print("Results:")
        print("=" * 80)
        
        # Display results
        print(f"\n✓ Generated {len(result['layout_graphs'])} layout(s)")
        print(f"✓ Canvas size: {result['canvas_size']}")
        print(f"✓ Labels used: {result['labels']}")
        print(f"✓ Number of design intent bboxes: {len(result['design_intent_bboxes'])}")
        
        # Display layout graph details
        if result['layout_graphs']:
            layout = result['layout_graphs'][0]
            print(f"\n✓ Layout Graph:")
            print(f"  - Number of elements: {len(layout.get('cls_elem', []))}")
            print(f"  - Classes: {layout.get('cls_elem', [])}")
            
            if layout.get('box_elem'):
                print(f"  - Bounding boxes:")
                for i, box in enumerate(layout['box_elem'][:5]):  # Show first 5
                    print(f"    Element {i+1}: {box}")
                if len(layout['box_elem']) > 5:
                    print(f"    ... and {len(layout['box_elem']) - 5} more")
        
        # Display SVG (first 500 chars)
        if result['svg_results']:
            svg = result['svg_results'][0]
            print(f"\n✓ Generated SVG (first 500 chars):")
            print(f"  {svg[:500]}...")
            if len(svg) > 500:
                print(f"  ... (total length: {len(svg)} chars)")
        
        # Visualize the layout on the image
        if not no_vis:
            print("\n" + "=" * 80)
            print("Creating Visualization...")
            print("=" * 80)
            
            try:
                if result['layout_graphs'] and result['svg_results']:
                    layout = result['layout_graphs'][0]
                    svg = result['svg_results'][0]
                    
                    output_path = visualize_layout_on_image(
                        image_path=str(test_image_path),
                        svg_string=svg,
                        layout_graph=layout,
                        label_info=dataset_info['label_info'],
                        canvas_size=result['canvas_size'],
                        show_design_intent=result['design_intent_bboxes']
                    )
                    
                    print(f"✓ Visualization created successfully!")
                else:
                    print("⚠ No layout graphs or SVG results to visualize")
            except Exception as e:
                print(f"⚠ Could not create visualization: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n⚠ Visualization skipped (--no-vis flag)")
        
        print("\n" + "=" * 80)
        print("✓ Test completed successfully!")
        print("=" * 80)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: File not found: {e}")
        print("  Please check that the dataset directories exist and paths are correct.")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_with_custom_bboxes():
    """Test pipeline with custom bounding boxes."""
    print("\n" + "=" * 80)
    print("Testing with Custom Bounding Boxes")
    print("=" * 80)
    
    script_dir = Path(__file__).parent.parent
    test_image_path = script_dir / "test.png"
    
    if not test_image_path.exists():
        print(f"ERROR: Test image not found at {test_image_path}")
        return False
    
    img_size = get_image_size(str(test_image_path))
    
    # Custom bounding boxes - adjust these based on your image
    # Format: [(x1, y1, x2, y2), ...]
    custom_bboxes = [
        (50, 50, 450, 150),    # Top region
        (50, 200, 450, 500),   # Middle region
        (200, 600, 350, 700),  # Bottom region (smaller, for logo)
    ]
    
    print(f"\nUsing custom bounding boxes:")
    for i, bbox in enumerate(custom_bboxes):
        print(f"  Box {i+1}: ({bbox[0]}, {bbox[1]}) -> ({bbox[2]}, {bbox[3]})")
    
    # You can add more tests here with different configurations
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the layout generation pipeline')
    parser.add_argument('--image', type=str, default=None,
                       help='Path to test image (default: test.png in project root)')
    parser.add_argument('--dataset', type=str, default='movie-poster',
                       choices=['movie-poster', 'chinese-poem', 'food-menu', 'kind-animals', 
                               'london-subway', 'motivational-quote', 'travel-vintage'],
                       help='Dataset category to use')
    parser.add_argument('--simple', action='store_true',
                       help='Run a simple test without full dataset setup')
    parser.add_argument('--no-vis', action='store_true',
                       help='Skip visualization (faster testing)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("Layout Generation Pipeline Test Script")
    print("=" * 80)
    print("\nThis script tests the layout generation pipeline")
    print("Make sure you have:")
    print("  1. Test image (test.png in project root or specify with --image)")
    print("  2. Dataset directories properly configured")
    print("  3. LLM API key set (POE_API_KEY environment variable)")
    print("  4. Preprocessed dataset files available")
    print()
    
    if args.simple:
        print("Running simple test mode (basic functionality check)...")
        # Just check if imports work and basic structure is correct
        try:
            from pipeline import LayoutGenerationPipeline
            print("✓ Pipeline module imported successfully")
            print("✓ Basic test passed - module structure is correct")
            print("\nFor full testing, run without --simple flag")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    # Get image path
    image_path = args.image
    if image_path:
        image_path = Path(image_path)
        if not image_path.is_absolute():
            image_path = Path(__file__).parent.parent / image_path
        image_path = str(image_path)
    
    # Run basic test
    success = test_pipeline_basic(image_path=image_path, dataset_category=args.dataset, no_vis=args.no_vis)
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTips:")
        print("  - Check that dataset directories exist")
        print("  - Verify LLM API key is set: echo $POE_API_KEY")
        print("  - Ensure preprocessed .pt files are available")
        print("  - Try running with --simple flag first to check imports")
        sys.exit(1)
