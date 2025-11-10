"""Experimental comparison: Baseline vs LoRA"""
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.pipeline import Key2PosterPipeline
from src.evaluator import PosterEvaluator
import time

def run_baseline_experiment(test_keywords, output_dir="outputs/baseline"):
    """Run baseline SD experiment"""
    print("\n" + "="*60)
    print("BASELINE EXPERIMENT: Vanilla Stable Diffusion")
    print("="*60)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pipeline = Key2PosterPipeline(use_lora=False)
    
    results = []
    for i, keywords in enumerate(test_keywords):
        print(f"\n--- Test {i+1}/{len(test_keywords)} ---")
        output_path = f"{output_dir}/poster_{i}.png"
        image, brief, metrics = pipeline.generate_poster(keywords, output_path, seed=42+i)
        
        results.append({
            "keywords": keywords,
            "brief": brief,
            "metrics": metrics,
            "path": output_path
        })
    
    # Save results
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def run_lora_experiment(test_keywords, lora_path, output_dir="outputs/lora"):
    """Run LoRA-enhanced experiment"""
    print("\n" + "="*60)
    print("LORA EXPERIMENT: Fine-tuned Stable Diffusion")
    print("="*60)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pipeline = Key2PosterPipeline(lora_path=lora_path, use_lora=True)
    
    results = []
    for i, keywords in enumerate(test_keywords):
        print(f"\n--- Test {i+1}/{len(test_keywords)} ---")
        output_path = f"{output_dir}/poster_{i}.png"
        image, brief, metrics = pipeline.generate_poster(keywords, output_path, seed=42+i)
        
        results.append({
            "keywords": keywords,
            "brief": brief,
            "metrics": metrics,
            "path": output_path
        })
    
    # Save results
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def compare_results(baseline_results, lora_results):
    """Compare baseline vs LoRA results"""
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    
    for i, (base, lora) in enumerate(zip(baseline_results, lora_results)):
        print(f"\nTest {i+1}: {base['keywords']}")
        print(f"  Baseline aesthetic: {base['metrics']['aesthetic']['overall']:.3f}")
        print(f"  LoRA aesthetic:     {lora['metrics']['aesthetic']['overall']:.3f}")
        improvement = lora['metrics']['aesthetic']['overall'] - base['metrics']['aesthetic']['overall']
        print(f"  Improvement:        {improvement:+.3f}")

if __name__ == "__main__":
    # Test keywords covering different genres
    test_keywords = [
        "space exploration adventure",
        "dark fantasy warrior",
        "romantic sunset beach",
        "cyberpunk city night",
        "horror haunted mansion"
    ]
    
    # Run baseline
    baseline_results = run_baseline_experiment(test_keywords)
    
    # Run LoRA (if available)
    lora_path = "models/poster_lora"
    if Path(lora_path).exists():
        lora_results = run_lora_experiment(test_keywords, lora_path)
        compare_results(baseline_results, lora_results)
    else:
        print(f"\nLoRA model not found at {lora_path}. Skipping LoRA experiment.")
        print("Train LoRA first using: python src/train_lora.py")
