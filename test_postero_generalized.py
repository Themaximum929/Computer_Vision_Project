"""Test PosterO Generalized Layout Generation"""
from src.postero_generalized import PosterOGeneralized

def test_single_category():
    """Test layout generation for one category"""
    print("Testing PosterO Generalized Layout Generation...")
    
    generator = PosterOGeneralized(
        llm_path="/home/themaximum/models/mistral-7b-instruct",
        dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
    )
    
    # Test movie-poster category
    print("\nGenerating layout for movie-poster...")
    layout = generator.generate_layout(
        category="movie-poster",
        num_elements=3,
        sample_size=5  # Small for testing
    )
    
    print(f"Generated layout:")
    print(f"  Canvas size: {layout['canvas_size']}")
    print(f"  Elements: {len(layout['bboxes'])}")
    print(f"  Labels: {layout['labels']}")
    print(f"  Bboxes: {layout['bboxes']}")
    print(f"  SVG:\n{layout['svg'][:200]}...")

def test_all_categories():
    """Test all 7 categories"""
    print("Testing all PStylish7 categories...")
    
    generator = PosterOGeneralized(
        llm_path="/home/themaximum/models/mistral-7b-instruct",
        dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
    )
    
    results = generator.batch_generate(
        categories=['movie-poster', 'motivational-quote'],  # Test subset
        num_elements=3,
        sample_size=5
    )
    
    for cat, layout in results.items():
        if layout:
            print(f"\n{cat}: ✓ Generated {len(layout['bboxes'])} elements")
        else:
            print(f"\n{cat}: ✗ Failed")

if __name__ == "__main__":
    # Mistral path is already configured
    print("Ready to test! Run test_single_category() or test_all_categories()")
    print(f"Using Mistral at: /home/themaximum/models/mistral-7b-instruct")
    print("\nAvailable categories:")
    for cat, desc in PosterOGeneralized.CATEGORIES.items():
        print(f"  - {cat}: {desc}")
