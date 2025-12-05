#!/usr/bin/env python3
"""Test PosterO Underlay Mode"""

from src.pipeline_postero_underlay import Key2PosterUnderlayMode

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
    print("Testing PosterO Underlay Mode")
    print("="*60)
    
    for i, test_case in enumerate(TEST_CASES):
        print(f"\n\nTest {i+1}/{len(TEST_CASES)}")
        print("-" * 60)
        
        pipeline = Key2PosterUnderlayMode(
            poster_type=test_case['type'],
            style_preset=test_case['style']
        )
        
        output_path = f"outputs/underlay_test_{i+1}.png"
        image, brief, metrics = pipeline.generate_poster(
            keywords=test_case['keywords'],
            output_path=output_path,
            seed=42 + i
        )
        
        print(f"\n✓ Test {i+1} complete!")
        print(f"  Output: {output_path}")
        print(f"  Layout: {output_path.replace('.png', '_layout.svg')}")
    
    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60)

if __name__ == "__main__":
    main()
