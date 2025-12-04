"""
Test script to compare base FLUX (direct user input) vs FluxPipeline (enhanced prompt)
and evaluate with CLIP scores against standard poster type targets.
"""

import os
import time
from pathlib import Path
from src.visual_generator_flux import VisualGeneratorFlux
from src.pipeline import Key2PosterPipeline
from src.clip_evaluator_LLC import CLIPEvaluatorLLC, compare_images


def get_target_string(poster_type: str) -> str:
    """Get standard target string for CLIP evaluation based on poster type"""
    targets = {
        "movie": "movie poster",
        "book": "book cover poster",
        "event": "event poster",
        "product": "product advertisement poster",
        "music": "music album poster",
        "game": "video game poster",
        "theater": "theater play poster",
        "conference": "conference poster",
        "festival": "festival poster"
    }
    return targets.get(poster_type.lower(), "poster")


def test_flux_comparison(
    user_input: str,
    poster_type: str = "movie",
    img_size: tuple = (720, 1072),
    seed: int = None,
    output_dir: str = "evaluate"
):
    """
    Compare base FLUX (direct input) vs FluxPipeline (enhanced prompt) with CLIP evaluation.
    
    Args:
        user_input: Original user keywords (e.g., "anime war girl gun battle")
        poster_type: Type of poster (movie, book, etc.)
        img_size: Image dimensions (width, height)
        seed: Random seed for reproducibility
        output_dir: Directory to save outputs
    """
    print("\n" + "="*70)
    print("FLUX BASE MODEL vs FLUX PIPELINE - CLIP EVALUATION TEST")
    print("="*70)
    print(f"User Input: {user_input}")
    print(f"Poster Type: {poster_type}")
    print(f"Image Size: {img_size}")
    print(f"Seed: {seed if seed else 'Random'}")
    print("="*70 + "\n")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    
    # Get target string for CLIP evaluation
    target_string = f'{get_target_string(poster_type)} with clear text description'
    print(f"[INFO] Target string for CLIP evaluation: '{target_string}'\n")
    
    # Initialize CLIP evaluator
    print("[1/5] Initializing CLIP Evaluator...")
    evaluator = CLIPEvaluatorLLC()
    print("✓ CLIP Evaluator ready\n")
    
    # Method 1: Generate with base FLUX using direct user input (no pipeline)
    print("[2/5] Generating poster with BASE FLUX (direct user input)...")
    base_flux_output = os.path.join(output_dir, f"base_flux_{timestamp}.png")
    
    base_generator = VisualGeneratorFlux(model_id="black-forest-labs/FLUX.1-schnell")
    
    # Add "poster" to the base prompt for fair comparison
    base_prompt = f"{user_input} poster"
    print(f"  Base prompt: {base_prompt}")
    
    # Use original user input with poster keyword (no enhancement, no pipeline)
    base_flux_image = base_generator.generate(
        prompt=base_prompt,
        width=img_size[0],
        height=img_size[1],
        seed=seed
    )
    
    base_flux_image.save(base_flux_output, quality=95)
    print(f"✓ Base FLUX poster saved to: {base_flux_output}\n")
    
    # Method 2: Generate with Pipeline (which includes concept expansion)
    print("[3/5] Generating poster with PIPELINE (with built-in concept expansion)...")
    pipeline_output = os.path.join(output_dir, f"pipeline_flux_{timestamp}.png")
    
    # Initialize pipeline with FLUX enabled
    pipeline = Key2PosterPipeline(
        use_flux=True,
        flux_model="black-forest-labs/FLUX.1-schnell",
        poster_type=poster_type,
        remove_text=False,  # Keep original image
        super_resolution=False,  # Faster for testing
        add_title=True,
        use_template=True
    )
    
    # Generate poster - pipeline will internally:
    # 1. Expand concepts using ConceptExpander
    # 2. Generate FLUX image with enhanced prompt
    # 3. Return the FLUX image in brief['flux_image']
    pipeline_image, brief, _ = pipeline.generate_poster(
        keywords=user_input,
        output_path=None,  # We'll save manually
        seed=seed,
        evaluate=False
    )
    
    pipeline_image.save(pipeline_output, quality=95)
    
    # Get the enhanced prompt that was used
    enhanced_prompt = brief.get('description', user_input)
    print(f"✓ Enhanced prompt used: {enhanced_prompt[:100]}...")
    print(f"✓ Pipeline FLUX poster saved to: {pipeline_output}\n")
    
    # Step 4: Compare both images with CLIP against target string
    print("[4/5] Comparing images with CLIP against target string...")
    
    # Use the new compare_images function
    comparison_result = evaluator.compare_images(
        image1_path=base_flux_output,
        image2_path=pipeline_output,
        target_string=target_string
    )
    
    base_flux_score = comparison_result['image1_score']
    pipeline_score = comparison_result['image2_score']
    score_difference = comparison_result['difference']
    improvement_percentage = comparison_result['improvement_percentage']
    
    # Step 5: Generate detailed comparison report
    print("[5/5] Generating detailed comparison report...")
    
    # Print comparison summary
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    print(f"\nTarget String: '{target_string}'")
    print(f"\n{'Method':<30} {'CLIP Score':<15} {'Difference':<15}")
    print("-"*70)
    print(f"{'Base FLUX (direct input)':<30} {base_flux_score:<15.2f} {'-':<15}")
    print(f"{'Pipeline FLUX (enhanced)':<30} {pipeline_score:<15.2f} {score_difference:+.2f}")
    print("-"*70)
    print(f"\nImprovement: {score_difference:+.2f} ({improvement_percentage:+.1f}%)")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if score_difference > 0:
        print(f"✓ Pipeline FLUX (enhanced prompt) performs BETTER")
        print(f"  Improvement: +{score_difference:.2f} CLIP score ({improvement_percentage:+.1f}%)")
        print(f"  The enhanced prompt better matches the '{target_string}' target")
    elif score_difference < 0:
        print(f"✗ Base FLUX (direct input) performs BETTER")
        print(f"  Difference: {score_difference:.2f} CLIP score ({improvement_percentage:.1f}%)")
        print(f"  The direct input better matches the '{target_string}' target")
    else:
        print("≈ Both methods perform similarly")
    
    print("\n" + "="*70)
    print(f"Output files:")
    print(f"  Base FLUX: {base_flux_output}")
    print(f"  Pipeline FLUX: {pipeline_output}")
    print("="*70 + "\n")
    
    # Return results
    return {
        'user_input': user_input,
        'base_prompt': base_prompt,
        'enhanced_prompt': enhanced_prompt,
        'target_string': target_string,
        'base_flux_score': base_flux_score,
        'pipeline_score': pipeline_score,
        'score_difference': score_difference,
        'improvement_percentage': improvement_percentage,
        'base_flux_output': base_flux_output,
        'pipeline_output': pipeline_output
    }


if __name__ == "__main__":
    # # Test with example keywords
    # test_keywords = ""
    # poster_type = "movie"
    
    # result = test_flux_comparison(
    #     user_input=test_keywords,
    #     poster_type=poster_type,
    #     img_size=(720, 1072),
    #     seed=42  # Use fixed seed for reproducibility
    # )
    
    # print("\nTest completed! Check the evaluate/ directory for generated posters.")
    # print(f"\nResults:")
    # print(f"  Base FLUX Score: {result['base_flux_score']:.2f}")
    # print(f"  Pipeline FLUX Score: {result['pipeline_score']:.2f}")
    # print(f"  Improvement: {result['score_difference']:+.2f} ({result['improvement_percentage']:+.1f}%)")
    
    comparison_result = compare_images(
        image1_path="evaluate/base_flux_1764349745.png",
        image2_path="evaluate/pipeline_flux_1764349745.png",
        target_string="movie poster with clear text description"
    )
