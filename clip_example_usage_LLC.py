"""
CLIP Score Evaluation - Example Usage
Author: LLC (Liu Lichao)
"""

from src.clip_evaluator_LLC import CLIPEvaluatorLLC


if __name__ == "__main__":
    # Initialize
    evaluator = CLIPEvaluatorLLC()
    result = evaluator.compare_prompts(
        image="test_images_LLC/hamburger_pizza_1.jpg",
        original_prompt="hamburger and pizza",
        enhanced_prompt="A vibrant digital watercolor scene of a cozy diner table, "
                       "steam rising from a juicy hamburger beside a bubbling cheese pizza, "
                       "golden light reflecting off chrome surfaces, "
                       "evoking warmth and nostalgic hunger."
    )
    # Print results
    print(f"\nOriginal Score: {result['original_score']:.2f}")
    print(f"Enhanced Score: {result['enhanced_score']:.2f}")
    print(f"Improvement: {result['improvement']:+.2f}")
    print(f"Improvement %: {result['improvement_percentage']:+.1f}%")
