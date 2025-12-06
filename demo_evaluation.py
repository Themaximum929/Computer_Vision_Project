"""
Quick Demo: Generate sample evaluation data and visualize
For demonstration purposes without running full pipeline
"""

import json
import os
import numpy as np

def generate_demo_data():
    """Generate realistic demo evaluation data"""
    
    # Simulated metrics based on expected performance
    metrics = {
        "template": {
            "alignment_score": {"mean": 0.892, "std": 0.045, "min": 0.834, "max": 0.945},
            "overlap_ratio": {"mean": 0.043, "std": 0.021, "min": 0.018, "max": 0.078},
            "balance_score": {"mean": 0.756, "std": 0.089, "min": 0.645, "max": 0.867},
            "color_harmony": {"mean": 0.678, "std": 0.112, "min": 0.534, "max": 0.823},
            "contrast_score": {"mean": 0.623, "std": 0.134, "min": 0.456, "max": 0.789},
            "text_readability": {"mean": 0.712, "std": 0.098, "min": 0.589, "max": 0.834},
            "text_coverage": {"mean": 0.834, "std": 0.076, "min": 0.723, "max": 0.912}
        },
        "layoutgan": {
            "alignment_score": {"mean": 0.847, "std": 0.078, "min": 0.734, "max": 0.923},
            "overlap_ratio": {"mean": 0.067, "std": 0.034, "min": 0.023, "max": 0.112},
            "balance_score": {"mean": 0.812, "std": 0.067, "min": 0.712, "max": 0.889},
            "color_harmony": {"mean": 0.701, "std": 0.098, "min": 0.578, "max": 0.845},
            "contrast_score": {"mean": 0.689, "std": 0.121, "min": 0.534, "max": 0.823},
            "text_readability": {"mean": 0.745, "std": 0.087, "min": 0.634, "max": 0.856},
            "text_coverage": {"mean": 0.789, "std": 0.091, "min": 0.667, "max": 0.889}
        },
        "postero": {
            "alignment_score": {"mean": 0.923, "std": 0.032, "min": 0.878, "max": 0.967},
            "overlap_ratio": {"mean": 0.018, "std": 0.009, "min": 0.005, "max": 0.034},
            "balance_score": {"mean": 0.834, "std": 0.054, "min": 0.756, "max": 0.901},
            "color_harmony": {"mean": 0.745, "std": 0.076, "min": 0.645, "max": 0.867},
            "contrast_score": {"mean": 0.734, "std": 0.098, "min": 0.612, "max": 0.856},
            "text_readability": {"mean": 0.801, "std": 0.065, "min": 0.712, "max": 0.889},
            "text_coverage": {"mean": 0.867, "std": 0.054, "min": 0.789, "max": 0.934}
        }
    }
    
    performance = {
        "template": {
            "mean_time": 10.3,
            "std_time": 1.2,
            "peak_memory_mb": 2100
        },
        "layoutgan": {
            "mean_time": 18.7,
            "std_time": 2.1,
            "peak_memory_mb": 2800
        },
        "postero": {
            "mean_time": 28.4,
            "std_time": 3.5,
            "peak_memory_mb": 3400
        }
    }
    
    return metrics, performance

def main():
    print("Generating demo evaluation data...")
    
    os.makedirs("outputs/evaluation", exist_ok=True)
    
    metrics, performance = generate_demo_data()
    
    # Save to files
    with open("outputs/evaluation/metrics_comparison.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    with open("outputs/evaluation/performance_comparison.json", 'w') as f:
        json.dump(performance, f, indent=2)
    
    print("✓ Demo data saved to outputs/evaluation/")
    print("\nNow run: python visualize_evaluation.py")
    
    # Print quick summary
    print("\n" + "="*60)
    print("DEMO EVALUATION SUMMARY")
    print("="*60)
    
    print("\nKey Findings:")
    print("1. PosterO achieves highest quality (+12% vs Template)")
    print("2. Template offers best speed (3× faster than PosterO)")
    print("3. LayoutGAN provides adaptive layouts (+7% balance)")
    print("4. Overlap is lowest in PosterO (0.018 vs 0.043)")
    print("5. All methods maintain >0.7 readability score")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
