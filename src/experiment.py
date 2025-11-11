"""Baseline vs LoRA comparison experiments"""
import json
from pathlib import Path
from src.pipeline import Key2PosterPipeline
import time

def run_comparison_experiment(test_keywords, output_dir="outputs/comparison", seed=42):
    """Run controlled comparison between baseline and LoRA"""
    
    results = {
        "baseline": [],
        "lora": [],
        "test_cases": test_keywords
    }
    
    # Baseline experiments
    print("\n" + "="*60)
    print("BASELINE EXPERIMENTS (Stable Diffusion v1.5)")
    print("="*60)
    baseline_pipeline = Key2PosterPipeline(use_lora=False)
    
    for i, keywords in enumerate(test_keywords):
        print(f"\n[Baseline {i+1}/{len(test_keywords)}] Keywords: {keywords}")
        output_path = f"{output_dir}/baseline/poster_{i}.png"
        start = time.time()
        image, brief, metrics = baseline_pipeline.generate_poster(keywords, output_path, seed=seed+i)
        elapsed = time.time() - start
        
        results["baseline"].append({
            "keywords": keywords,
            "brief": brief,
            "metrics": metrics,
            "time": elapsed,
            "path": output_path
        })
    
    # LoRA experiments
    print("\n" + "="*60)
    print("LORA EXPERIMENTS (Fine-tuned on Movie Posters)")
    print("="*60)
    lora_pipeline = Key2PosterPipeline(lora_path="models/poster_lora", use_lora=True)
    
    for i, keywords in enumerate(test_keywords):
        print(f"\n[LoRA {i+1}/{len(test_keywords)}] Keywords: {keywords}")
        output_path = f"{output_dir}/lora/poster_{i}.png"
        start = time.time()
        image, brief, metrics = lora_pipeline.generate_poster(keywords, output_path, seed=seed+i)
        elapsed = time.time() - start
        
        results["lora"].append({
            "keywords": keywords,
            "brief": brief,
            "metrics": metrics,
            "time": elapsed,
            "path": output_path
        })
    
    # Save results
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    
    baseline_avg = sum(r["metrics"]["aesthetic"]["overall"] for r in results["baseline"]) / len(results["baseline"])
    lora_avg = sum(r["metrics"]["aesthetic"]["overall"] for r in results["lora"]) / len(results["lora"])
    
    print(f"\nBaseline Average Aesthetic Score: {baseline_avg:.3f}")
    print(f"LoRA Average Aesthetic Score: {lora_avg:.3f}")
    print(f"Improvement: {((lora_avg - baseline_avg) / baseline_avg * 100):.1f}%")
    
    print(f"\nResults saved to {output_dir}/results.json")
    return results

if __name__ == "__main__":
    test_keywords = [
        "space exploration adventure",
        "dark fantasy warrior",
        "romantic sunset beach",
        "cyberpunk city noir",
        "epic battle scene"
    ]
    
    run_comparison_experiment(test_keywords)
