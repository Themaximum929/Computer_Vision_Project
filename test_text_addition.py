#!/usr/bin/env python3
"""Quick test of text addition to existing results"""

from add_text_to_poster import add_text_to_poster

# Test with existing result_1
add_text_to_poster(
    image_path="test_image_1.png",
    svg_path="result_1_output.svg",
    title="ALPINE ADVENTURE",
    captions=["Discover Switzerland", "Summer 2024"],
    output_path="result_1_final_test.png"
)

print("\n✓ Test complete! Check result_1_final_test.png")
