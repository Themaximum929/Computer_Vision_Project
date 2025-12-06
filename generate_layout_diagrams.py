"""
Generate Visual Diagrams for Layout Documentation
Creates architecture diagrams, flow charts, and layout patterns
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_architecture_diagram():
    """Generate three-tier architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(7, 7.5, 'Three-Tier Layout Architecture', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # Three columns
    methods = [
        ('Template Mode', 'Rule-Based', '6 Patterns', '~10s', '0.75', '#3498db'),
        ('LayoutGAN Mode', 'AI-Optimized', 'CLG-LO', '~19s', '0.78', '#e74c3c'),
        ('PosterO Mode', 'Content-Aware', 'CNN + LLM', '~28s', '0.84', '#2ecc71')
    ]
    
    x_positions = [2, 7, 12]
    
    for i, (name, method, tech, time, quality, color) in enumerate(methods):
        x = x_positions[i]
        
        # Main box
        box = FancyBboxPatch((x-1.5, 3), 3, 3, 
                             boxstyle="round,pad=0.1", 
                             edgecolor=color, facecolor=color, alpha=0.2, linewidth=3)
        ax.add_patch(box)
        
        # Text
        ax.text(x, 5.5, name, ha='center', va='center', 
                fontsize=12, fontweight='bold', color=color)
        ax.text(x, 5, method, ha='center', va='center', fontsize=10)
        ax.text(x, 4.5, tech, ha='center', va='center', fontsize=9, style='italic')
        ax.text(x, 4, f'Time: {time}', ha='center', va='center', fontsize=9)
        ax.text(x, 3.5, f'Quality: {quality}', ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Input/Output
    ax.text(7, 2, 'Input: Keywords + Poster Type + Style', 
            ha='center', va='center', fontsize=11, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.text(7, 1, 'Output: 720×1280 Poster with Optimized Layout', 
            ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    # Arrows
    for x in x_positions:
        arrow = FancyArrowPatch((x, 3), (x, 2.3),
                               arrowstyle='->', mutation_scale=20, 
                               linewidth=2, color='gray')
        ax.add_patch(arrow)
        
        arrow2 = FancyArrowPatch((x, 1.7), (x, 1.3),
                                arrowstyle='->', mutation_scale=20,
                                linewidth=2, color='gray')
        ax.add_patch(arrow2)
    
    plt.tight_layout()
    plt.savefig('outputs/evaluation/architecture_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Architecture diagram saved")
    plt.close()

def create_layout_patterns():
    """Generate 6 layout pattern visualizations"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Template Layout Patterns', fontsize=16, fontweight='bold')
    
    patterns = [
        ('Split', [(0.1, 0.5, 0.8, 0.4), (0.1, 0.1, 0.8, 0.3)]),
        ('Grid', [(0.1, 0.4, 0.8, 0.5), (0.1, 0.1, 0.8, 0.2)]),
        ('Hero', [(0.1, 0.3, 0.8, 0.6), (0.1, 0.1, 0.8, 0.15)]),
        ('Sidebar', [(0.1, 0.1, 0.5, 0.8), (0.65, 0.3, 0.25, 0.4)]),
        ('Asymmetric', [(0.2, 0.3, 0.6, 0.6), (0.1, 0.1, 0.7, 0.15)]),
        ('Minimal', [(0.15, 0.35, 0.7, 0.5), (0.15, 0.1, 0.7, 0.2)])
    ]
    
    for idx, (name, boxes) in enumerate(patterns):
        ax = axes[idx // 3, idx % 3]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(name, fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Background
        bg = patches.Rectangle((0, 0), 1, 1, linewidth=2, 
                              edgecolor='black', facecolor='white')
        ax.add_patch(bg)
        
        # Image region (first box)
        img_box = patches.Rectangle((boxes[0][0], boxes[0][1]), 
                                    boxes[0][2], boxes[0][3],
                                    linewidth=2, edgecolor='#3498db', 
                                    facecolor='#3498db', alpha=0.3)
        ax.add_patch(img_box)
        ax.text(boxes[0][0] + boxes[0][2]/2, 
               boxes[0][1] + boxes[0][3]/2,
               'IMAGE', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='#3498db')
        
        # Text region (second box)
        text_box = patches.Rectangle((boxes[1][0], boxes[1][1]), 
                                     boxes[1][2], boxes[1][3],
                                     linewidth=2, edgecolor='#e74c3c', 
                                     facecolor='#e74c3c', alpha=0.3)
        ax.add_patch(text_box)
        ax.text(boxes[1][0] + boxes[1][2]/2, 
               boxes[1][1] + boxes[1][3]/2,
               'TEXT', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='#e74c3c')
    
    plt.tight_layout()
    plt.savefig('outputs/evaluation/layout_patterns.png', dpi=300, bbox_inches='tight')
    print("✓ Layout patterns saved")
    plt.close()

def create_pipeline_flow():
    """Generate pipeline flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'PosterO Pipeline Flow', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Stages
    stages = [
        (6, 8.5, 'User Input\nKeywords', '#95a5a6'),
        (6, 7.5, 'LLM Enhancement\n(POE API)', '#3498db'),
        (6, 6.5, 'FLUX.1 Generation\n512×768', '#9b59b6'),
        (6, 5.5, 'Resize to 513×750\n(PosterO Input)', '#95a5a6'),
        (3, 4, 'Stage 1: CNN\nDesign Intent\nDetection', '#e74c3c'),
        (9, 4, 'Stage 2: LLM\nLayout Generation\n(POE API)', '#2ecc71'),
        (6, 2.5, 'Upscale to 720×1280\nScale Bboxes', '#95a5a6'),
        (6, 1.5, 'Text Rendering\nFinal Poster', '#f39c12'),
    ]
    
    for x, y, text, color in stages:
        width = 2.5 if 'Stage' in text else 2
        box = FancyBboxPatch((x-width/2, y-0.3), width, 0.6,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, 
                            alpha=0.3, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Arrows
    arrows = [
        (6, 8.2, 6, 7.8),
        (6, 7.2, 6, 6.8),
        (6, 6.2, 6, 5.8),
        (6, 5.2, 3, 4.3),
        (6, 5.2, 9, 4.3),
        (3, 3.7, 6, 2.8),
        (9, 3.7, 6, 2.8),
        (6, 2.2, 6, 1.8),
    ]
    
    for x1, y1, x2, y2 in arrows:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=15,
                               linewidth=2, color='gray')
        ax.add_patch(arrow)
    
    # Annotations
    ax.text(1.5, 4, 'Available\nAreas', ha='center', va='center',
           fontsize=8, style='italic', color='#e74c3c')
    ax.text(10.5, 4, 'SVG\nLayout', ha='center', va='center',
           fontsize=8, style='italic', color='#2ecc71')
    
    plt.tight_layout()
    plt.savefig('outputs/evaluation/pipeline_flow.png', dpi=300, bbox_inches='tight')
    print("✓ Pipeline flow saved")
    plt.close()

def create_constraint_diagram():
    """Generate constraint visualization"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Layout Constraints', fontsize=16, fontweight='bold')
    
    # Rule of Thirds
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_title('Rule of Thirds', fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Grid lines
    for i in [1/3, 2/3]:
        ax.plot([i, i], [0, 1], 'r--', linewidth=2, alpha=0.7)
        ax.plot([0, 1], [i, i], 'r--', linewidth=2, alpha=0.7)
    
    # Focal points
    for x in [1/3, 2/3]:
        for y in [1/3, 2/3]:
            ax.plot(x, y, 'ro', markersize=10)
    
    ax.text(0.5, 0.05, 'Focal points at intersections', 
           ha='center', fontsize=9, style='italic')
    
    # Border Constraint
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_title('Border Constraint', fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Outer border
    outer = patches.Rectangle((0, 0), 1, 1, linewidth=3,
                             edgecolor='black', facecolor='white')
    ax.add_patch(outer)
    
    # Safe area
    margin = 0.07
    safe = patches.Rectangle((margin, margin), 1-2*margin, 1-2*margin,
                            linewidth=2, edgecolor='green', 
                            facecolor='green', alpha=0.2, linestyle='--')
    ax.add_patch(safe)
    
    ax.text(0.5, 0.03, '50px minimum margin', 
           ha='center', fontsize=9, style='italic', color='green')
    
    # Overlap Prevention
    ax = axes[2]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_title('Overlap Prevention', fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # Image box
    img = patches.Rectangle((0.1, 0.4), 0.8, 0.5, linewidth=2,
                           edgecolor='#3498db', facecolor='#3498db', alpha=0.3)
    ax.add_patch(img)
    ax.text(0.5, 0.65, 'IMAGE', ha='center', fontsize=10, 
           fontweight='bold', color='#3498db')
    
    # Text box (no overlap)
    text = patches.Rectangle((0.15, 0.1), 0.7, 0.2, linewidth=2,
                            edgecolor='#2ecc71', facecolor='#2ecc71', alpha=0.3)
    ax.add_patch(text)
    ax.text(0.5, 0.2, 'TEXT', ha='center', fontsize=10,
           fontweight='bold', color='#2ecc71')
    
    ax.text(0.5, 0.35, 'IoU < 0.1', ha='center', fontsize=9,
           style='italic', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('outputs/evaluation/constraint_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Constraint diagram saved")
    plt.close()

def main():
    import os
    os.makedirs('outputs/evaluation', exist_ok=True)
    
    print("Generating layout diagrams...")
    print("-" * 40)
    
    create_architecture_diagram()
    create_layout_patterns()
    create_pipeline_flow()
    create_constraint_diagram()
    
    print("-" * 40)
    print("✓ All diagrams generated successfully!")
    print("\nGenerated files:")
    print("  - outputs/evaluation/architecture_diagram.png")
    print("  - outputs/evaluation/layout_patterns.png")
    print("  - outputs/evaluation/pipeline_flow.png")
    print("  - outputs/evaluation/constraint_diagram.png")
    print("\nUse these in your report for visual clarity!")

if __name__ == "__main__":
    main()
