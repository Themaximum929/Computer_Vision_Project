"""
Visualize Comparative Evaluation Results
Generates charts for Layout and Composition report
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_results():
    """Load evaluation results"""
    with open("outputs/evaluation/metrics_comparison.json", 'r') as f:
        metrics = json.load(f)
    
    with open("outputs/evaluation/performance_comparison.json", 'r') as f:
        performance = json.load(f)
    
    return metrics, performance

def plot_comparative_charts():
    """Generate 6-panel visualization"""
    metrics, performance = load_results()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Comparative Evaluation: Template vs LayoutGAN vs PosterO', 
                 fontsize=16, fontweight='bold')
    
    methods = ['template', 'layoutgan', 'postero']
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    labels = ['Template', 'LayoutGAN', 'PosterO']
    
    # 1. Layout Quality Metrics
    ax = axes[0, 0]
    layout_metrics = ['alignment_score', 'overlap_ratio', 'balance_score']
    x = np.arange(len(layout_metrics))
    width = 0.25
    
    for i, method in enumerate(methods):
        if method not in metrics:
            continue
        values = [metrics[method][m]['mean'] for m in layout_metrics]
        errors = [metrics[method][m]['std'] for m in layout_metrics]
        ax.bar(x + i*width, values, width, label=labels[i], 
               color=colors[i], alpha=0.8, yerr=errors, capsize=5)
    
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Layout Quality Metrics', fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Alignment ↑', 'Overlap ↓', 'Balance ↑'], rotation=15)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # 2. Aesthetic Quality Metrics
    ax = axes[0, 1]
    aesthetic_metrics = ['color_harmony', 'contrast_score']
    x = np.arange(len(aesthetic_metrics))
    width = 0.25
    
    for i, method in enumerate(methods):
        if method not in metrics:
            continue
        values = [metrics[method][m]['mean'] for m in aesthetic_metrics]
        errors = [metrics[method][m]['std'] for m in aesthetic_metrics]
        ax.bar(x + i*width, values, width, label=labels[i], 
               color=colors[i], alpha=0.8, yerr=errors, capsize=5)
    
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Aesthetic Quality Metrics', fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Color Harmony ↑', 'Contrast ↑'], rotation=15)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # 3. Readability Metrics
    ax = axes[0, 2]
    readability_metrics = ['text_readability', 'text_coverage']
    x = np.arange(len(readability_metrics))
    width = 0.25
    
    for i, method in enumerate(methods):
        if method not in metrics:
            continue
        values = [metrics[method][m]['mean'] for m in readability_metrics]
        errors = [metrics[method][m]['std'] for m in readability_metrics]
        ax.bar(x + i*width, values, width, label=labels[i], 
               color=colors[i], alpha=0.8, yerr=errors, capsize=5)
    
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Readability Metrics', fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Text Readability ↑', 'Text Coverage ↑'], rotation=15)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # 4. Overall Score Radar Chart
    ax = axes[1, 0]
    categories = ['Alignment', 'Balance', 'Harmony', 'Contrast', 'Readability', 'Coverage']
    metric_keys = ['alignment_score', 'balance_score', 'color_harmony', 
                   'contrast_score', 'text_readability', 'text_coverage']
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax = plt.subplot(2, 3, 4, projection='polar')
    
    for i, method in enumerate(methods):
        if method not in metrics:
            continue
        values = [metrics[method][m]['mean'] for m in metric_keys]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=labels[i], color=colors[i])
        ax.fill(angles, values, alpha=0.15, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=9)
    ax.set_ylim(0, 1)
    ax.set_title('Overall Quality Profile', fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    # 5. Generation Time Comparison
    ax = axes[1, 1]
    x = np.arange(len(methods))
    times = [performance[m]['mean_time'] for m in methods if m in performance]
    errors = [performance[m]['std_time'] for m in methods if m in performance]
    
    bars = ax.bar(x, times, color=colors[:len(times)], alpha=0.8, yerr=errors, capsize=5)
    ax.set_ylabel('Time (seconds)', fontweight='bold')
    ax.set_title('Generation Time (Lower is Better)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([labels[i] for i in range(len(times))])
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    # 6. Memory Usage Comparison
    ax = axes[1, 2]
    x = np.arange(len(methods))
    memory = [performance[m]['peak_memory_mb'] for m in methods if m in performance]
    
    bars = ax.bar(x, memory, color=colors[:len(memory)], alpha=0.8)
    ax.set_ylabel('Memory (MB)', fontweight='bold')
    ax.set_title('Peak Memory Usage', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([labels[i] for i in range(len(memory))])
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, mem in zip(bars, memory):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mem:.0f}MB', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('outputs/evaluation/evaluation_charts.png', dpi=300, bbox_inches='tight')
    print("✓ Charts saved to outputs/evaluation/evaluation_charts.png")
    plt.show()

def print_summary_table():
    """Print formatted summary table"""
    metrics, performance = load_results()
    
    print("\n" + "="*80)
    print("COMPARATIVE EVALUATION SUMMARY")
    print("="*80)
    
    methods = ['template', 'layoutgan', 'postero']
    labels = ['Template', 'LayoutGAN', 'PosterO']
    
    metric_names = {
        'alignment_score': 'Alignment Score ↑',
        'overlap_ratio': 'Overlap Ratio ↓',
        'balance_score': 'Balance Score ↑',
        'color_harmony': 'Color Harmony ↑',
        'contrast_score': 'Contrast Score ↑',
        'text_readability': 'Text Readability ↑',
        'text_coverage': 'Text Coverage ↑'
    }
    
    # Print header
    print(f"\n{'Metric':<25} {'Template':<20} {'LayoutGAN':<20} {'PosterO':<20}")
    print("-"*85)
    
    # Print metrics
    for key, name in metric_names.items():
        row = f"{name:<25}"
        for method in methods:
            if method in metrics and key in metrics[method]:
                mean = metrics[method][key]['mean']
                std = metrics[method][key]['std']
                row += f"{mean:.3f} ± {std:.3f}      "
            else:
                row += "N/A                 "
        print(row)
    
    # Print performance
    print("-"*85)
    row = f"{'Generation Time (s)':<25}"
    for method in methods:
        if method in performance:
            mean = performance[method]['mean_time']
            std = performance[method]['std_time']
            row += f"{mean:.1f} ± {std:.1f}         "
        else:
            row += "N/A                 "
    print(row)
    
    row = f"{'Peak Memory (MB)':<25}"
    for method in methods:
        if method in performance:
            mem = performance[method]['peak_memory_mb']
            row += f"{mem:.0f}                  "
        else:
            row += "N/A                 "
    print(row)
    
    print("="*80)
    
    # Calculate overall winner
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    for i, method in enumerate(methods):
        if method not in metrics:
            continue
        
        # Calculate average score (excluding overlap which is inverse)
        scores = []
        for key in ['alignment_score', 'balance_score', 'color_harmony', 
                   'contrast_score', 'text_readability', 'text_coverage']:
            scores.append(metrics[method][key]['mean'])
        
        # Invert overlap (lower is better)
        overlap_score = 1 - metrics[method]['overlap_ratio']['mean']
        scores.append(overlap_score)
        
        avg_quality = np.mean(scores)
        
        print(f"\n{labels[i]}:")
        print(f"  Average Quality Score: {avg_quality:.3f}")
        if method in performance:
            print(f"  Generation Time: {performance[method]['mean_time']:.1f}s")
            print(f"  Quality/Time Ratio: {avg_quality/performance[method]['mean_time']:.4f}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    if not os.path.exists("outputs/evaluation/metrics_comparison.json"):
        print("Error: Run 'python run_comparative_evaluation.py' first!")
        exit(1)
    
    print("Generating visualization charts...")
    plot_comparative_charts()
    print_summary_table()
