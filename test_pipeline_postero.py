#!/usr/bin/env python3
"""Test Enhanced Key2Poster Pipeline with PosterO"""

from src.pipeline_postero import Key2PosterPosterO

# Test cases
TEST_CASES = [
    {
        "keywords": "vintage travel mountains",
        "type": "event",
        "style": "vintage"
    },
    {
        "keywords": "cyberpunk neon city",
        "type": "movie",
        "style": "neon"
    },
    {
        "keywords": "food restaurant elegant",
        "type": "product",
        "style": "minimalist"
    }
]

def main():
    print("\n" + "="*60)
    print("Testing Enhanced Key2Poster + PosterO Pipeline")
    print("="*60)
    
    for i, test_case in enumerate(TEST_CASES):
        print(f"\n\nTest {i+1}/{len(TEST_CASES)}")
        print("-" * 60)
        
        # Initialize pipeline
        pipeline = Key2PosterPosterO(
            poster_type=test_case['type'],
            style_preset=test_case['style']
        )
        
        # Generate poster
        output_path = f"outputs/pipeline_test_{i+1}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords=test_case['keywords'],
            output_path=output_path,
            seed=42 + i
        )
        
        print(f"\n✓ Test {i+1} complete!")
        print(f"  Output: {output_path}")
        print(f"  Layout: {output_path.replace('.png', '_layout.svg')}")
        print(f"  Visualization: {output_path.replace('.png', '_visualization.png')}")
    
    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60)

if __name__ == "__main__":
    main()
