"""Visualize comparison results between baseline and LoRA"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_comparison_grid(results_path="outputs/comparison/results.json", output_path="outputs/comparison_grid.png"):
    """Create side-by-side comparison grid"""
    
    if not Path(results_path).exists():
        print(f"Results not found at {results_path}")
        print("Run experiments first: python src/experiment.py")
        return
    
    with open(results_path) as f:
        results = json.load(f)
    
    baseline_results = results["baseline"]
    lora_results = results["lora"]
    
    if len(baseline_results) == 0 or len(lora_results) == 0:
        print("No results to visualize")
        return
    
    # Load images
    num_pairs = min(len(baseline_results), len(lora_results))
    
    # Create grid (2 columns: baseline, lora)
    img_width = 720
    img_height = 1280
    margin = 20
    text_height = 100
    
    grid_width = 2 * img_width + 3 * margin
    grid_height = num_pairs * (img_height + text_height + margin) + margin
    
    grid = Image.new('RGB', (grid_width, grid_height), color='white')
    draw = ImageDraw.Draw(grid)
    
    # Try to load font, fallback to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add headers
    draw.text((margin + img_width//2, margin//2), "BASELINE", fill='black', font=font_large, anchor="mm")
    draw.text((2*margin + img_width + img_width//2, margin//2), "LORA", fill='black', font=font_large, anchor="mm")
    
    # Add image pairs
    for i in range(num_pairs):
        y_offset = margin + i * (img_height + text_height + margin)
        
        # Baseline image
        baseline_path = baseline_results[i]["path"]
        if Path(baseline_path).exists():
            baseline_img = Image.open(baseline_path)
            grid.paste(baseline_img, (margin, y_offset))
            
            # Add metrics
            metrics = baseline_results[i]["metrics"]
            aesthetic = metrics["aesthetic"]["overall"]
            text = f"Aesthetic: {aesthetic:.3f}"
            draw.text((margin, y_offset + img_height + 10), text, fill='black', font=font_small)
        
        # LoRA image
        lora_path = lora_results[i]["path"]
        if Path(lora_path).exists():
            lora_img = Image.open(lora_path)
            grid.paste(lora_img, (2*margin + img_width, y_offset))
            
            # Add metrics
            metrics = lora_results[i]["metrics"]
            aesthetic = metrics["aesthetic"]["overall"]
            text = f"Aesthetic: {aesthetic:.3f}"
            draw.text((2*margin + img_width, y_offset + img_height + 10), text, fill='black', font=font_small)
        
        # Add keywords
        keywords = baseline_results[i]["keywords"]
        draw.text((margin, y_offset + img_height + 40), f"Keywords: {keywords}", fill='black', font=font_small)
    
    # Save grid
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    grid.save(output_path, quality=95)
    print(f"✓ Comparison grid saved to {output_path}")

def print_summary(results_path="outputs/comparison/results.json"):
    """Print summary statistics"""
    
    if not Path(results_path).exists():
        print(f"Results not found at {results_path}")
        return
    
    with open(results_path) as f:
        results = json.load(f)
    
    baseline_results = results["baseline"]
    lora_results = results["lora"]
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    # Calculate averages
    baseline_aesthetics = [r["metrics"]["aesthetic"]["overall"] for r in baseline_results]
    lora_aesthetics = [r["metrics"]["aesthetic"]["overall"] for r in lora_results]
    
    baseline_avg = sum(baseline_aesthetics) / len(baseline_aesthetics)
    lora_avg = sum(lora_aesthetics) / len(lora_aesthetics)
    
    baseline_times = [r["time"] for r in baseline_results]
    lora_times = [r["time"] for r in lora_results]
    
    baseline_time_avg = sum(baseline_times) / len(baseline_times)
    lora_time_avg = sum(lora_times) / len(lora_times)
    
    print(f"\nTest Cases: {len(baseline_results)}")
    print(f"\nBaseline:")
    print(f"  Average Aesthetic Score: {baseline_avg:.3f}")
    print(f"  Average Generation Time: {baseline_time_avg:.1f}s")
    
    print(f"\nLoRA:")
    print(f"  Average Aesthetic Score: {lora_avg:.3f}")
    print(f"  Average Generation Time: {lora_time_avg:.1f}s")
    
    improvement = ((lora_avg - baseline_avg) / baseline_avg * 100)
    print(f"\nImprovement:")
    print(f"  Aesthetic Score: {improvement:+.1f}%")
    print(f"  Generation Time: {((lora_time_avg - baseline_time_avg) / baseline_time_avg * 100):+.1f}%")
    
    print("\n" + "="*60)
    
    # Per-case breakdown
    print("\nPer-Case Results:")
    print("-"*60)
    for i in range(len(baseline_results)):
        keywords = baseline_results[i]["keywords"]
        baseline_score = baseline_aesthetics[i]
        lora_score = lora_aesthetics[i]
        improvement = ((lora_score - baseline_score) / baseline_score * 100)
        
        print(f"\n{i+1}. {keywords}")
        print(f"   Baseline: {baseline_score:.3f} | LoRA: {lora_score:.3f} | Δ: {improvement:+.1f}%")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize comparison results")
    parser.add_argument("--results", type=str, default="outputs/comparison/results.json", help="Results JSON path")
    parser.add_argument("--output", type=str, default="outputs/comparison_grid.png", help="Output grid image path")
    parser.add_argument("--no-grid", action="store_true", help="Skip grid generation")
    args = parser.parse_args()
    
    # Print summary
    print_summary(args.results)
    
    # Create comparison grid
    if not args.no_grid:
        print("\nGenerating comparison grid...")
        create_comparison_grid(args.results, args.output)

if __name__ == "__main__":
    main()
