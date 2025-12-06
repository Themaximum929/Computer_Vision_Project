"""
Run Comparative Evaluation of 3 Methods
Usage: python run_comparative_evaluation.py
"""

import os
from src.pipeline import Key2PosterPipeline
from src.pipeline_postero import Key2PosterPosterO
from src.comparative_evaluator import ComparativeEvaluator, benchmark_generation_time
import json

# Test keywords
TEST_KEYWORDS = [
    "cyberpunk neon city",
    "vintage travel mountains",
    "music festival summer",
    "space adventure astronaut",
    "food restaurant elegant"
]

def extract_layout_data(brief: dict, image_size=(720, 1280)):
    """Extract layout data from pipeline output"""
    layout = {}
    
    # Extract bboxes if available
    if 'title_bbox' in brief:
        layout['title_bbox'] = brief['title_bbox']
    if 'caption_bboxes' in brief:
        layout['caption_bboxes'] = brief['caption_bboxes']
    if 'image_bbox' in brief:
        layout['image_bbox'] = brief['image_bbox']
    else:
        # Estimate image region (assume top 60%)
        layout['image_bbox'] = (0, 0, image_size[0], int(image_size[1] * 0.6))
    
    return layout


def main():
    print("=" * 60)
    print("COMPARATIVE EVALUATION: Template vs LayoutGAN vs PosterO")
    print("=" * 60)
    
    evaluator = ComparativeEvaluator()
    performance = {}
    
    os.makedirs("outputs/evaluation", exist_ok=True)
    
    # 1. Template Mode
    print("\n[1/3] Evaluating Template Mode...")
    pipeline_template = Key2PosterPipeline(
        use_flux=True,
        use_template=True,
        add_title=True,
        poster_type='movie'
    )
    
    for i, keywords in enumerate(TEST_KEYWORDS):
        print(f"  Generating {i+1}/{len(TEST_KEYWORDS)}: {keywords}")
        output_path = f"outputs/evaluation/template_{i}.png"
        image, brief, metrics = pipeline_template.generate_poster(
            keywords=keywords,
            output_path=output_path,
            seed=42 + i
        )
        
        layout = extract_layout_data(brief)
        evaluator.evaluate_poster(output_path, layout, "template")
    
    performance['template'] = benchmark_generation_time(pipeline_template, TEST_KEYWORDS[0])
    
    # 2. LayoutGAN Mode
    print("\n[2/3] Evaluating LayoutGAN Mode...")
    pipeline_layoutgan = Key2PosterPipeline(
        use_flux=True,
        auto_template=True,
        add_title=True,
        poster_type='movie'
    )
    
    for i, keywords in enumerate(TEST_KEYWORDS):
        print(f"  Generating {i+1}/{len(TEST_KEYWORDS)}: {keywords}")
        output_path = f"outputs/evaluation/layoutgan_{i}.png"
        image, brief, metrics = pipeline_layoutgan.generate_poster(
            keywords=keywords,
            output_path=output_path,
            seed=42 + i
        )
        
        layout = extract_layout_data(brief)
        evaluator.evaluate_poster(output_path, layout, "layoutgan")
    
    performance['layoutgan'] = benchmark_generation_time(pipeline_layoutgan, TEST_KEYWORDS[0])
    
    # 3. PosterO Mode
    print("\n[3/3] Evaluating PosterO Mode...")
    try:
        pipeline_postero = Key2PosterPosterO(poster_type='movie')
        
        for i, keywords in enumerate(TEST_KEYWORDS):
            print(f"  Generating {i+1}/{len(TEST_KEYWORDS)}: {keywords}")
            output_path = f"outputs/evaluation/postero_{i}.png"
            image, brief, metrics = pipeline_postero.generate_poster(
                keywords=keywords,
                output_path=output_path,
                seed=42 + i
            )
            
            layout = extract_layout_data(brief)
            evaluator.evaluate_poster(output_path, layout, "postero")
        
        performance['postero'] = benchmark_generation_time(pipeline_postero, TEST_KEYWORDS[0])
    except Exception as e:
        print(f"  Warning: PosterO evaluation failed: {e}")
        print("  Skipping PosterO (may not be installed)")
    
    # Save results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    comparison = evaluator.compare_methods()
    
    # Print summary
    for method in ['template', 'layoutgan', 'postero']:
        if method not in comparison:
            continue
        
        print(f"\n{method.upper()}:")
        print(f"  Alignment Score:    {comparison[method]['alignment_score']['mean']:.3f} ± {comparison[method]['alignment_score']['std']:.3f}")
        print(f"  Overlap Ratio:      {comparison[method]['overlap_ratio']['mean']:.3f} ± {comparison[method]['overlap_ratio']['std']:.3f}")
        print(f"  Balance Score:      {comparison[method]['balance_score']['mean']:.3f} ± {comparison[method]['balance_score']['std']:.3f}")
        print(f"  Color Harmony:      {comparison[method]['color_harmony']['mean']:.3f} ± {comparison[method]['color_harmony']['std']:.3f}")
        print(f"  Contrast Score:     {comparison[method]['contrast_score']['mean']:.3f} ± {comparison[method]['contrast_score']['std']:.3f}")
        print(f"  Text Readability:   {comparison[method]['text_readability']['mean']:.3f} ± {comparison[method]['text_readability']['std']:.3f}")
        print(f"  Text Coverage:      {comparison[method]['text_coverage']['mean']:.3f} ± {comparison[method]['text_coverage']['std']:.3f}")
        
        if method in performance:
            print(f"  Generation Time:    {performance[method]['mean_time']:.2f}s ± {performance[method]['std_time']:.2f}s")
            print(f"  Peak Memory:        {performance[method]['peak_memory_mb']:.1f} MB")
    
    # Save to files
    evaluator.save_results("outputs/evaluation/metrics_comparison.json")
    
    with open("outputs/evaluation/performance_comparison.json", 'w') as f:
        json.dump(performance, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("Results saved to outputs/evaluation/")
    print("=" * 60)


if __name__ == "__main__":
    main()
