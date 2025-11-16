"""Test poster template composition"""
from src.pipeline import Key2PosterPipeline
from pathlib import Path

def test_simple_layout():
    """Test with simple layout (no template)"""
    print("=" * 70)
    print("TEST: Simple Layout Composition")
    print("=" * 70)
    
    pipeline = Key2PosterPipeline(
        baseline_style=True,
        add_title=True,
        use_template=True,  # Enable template composition
        template_path=None,  # No template = use simple layout
        remove_text=False,
        super_resolution=False
    )
    
    pipeline._current_genre = "scifi"
    
    output_path = "outputs/template_test/simple_layout.png"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    image, brief, metrics = pipeline.generate_poster(
        "space exploration adventure",
        output_path=output_path,
        seed=42,
        evaluate=True
    )
    
    print(f"\n✅ Simple layout test complete!")
    print(f"Saved to: {output_path}")
    print(f"Aesthetic score: {metrics['aesthetic']['overall']:.3f}")

def test_with_template():
    """Test with custom template (if available)"""
    print("\n" + "=" * 70)
    print("TEST: Custom Template Composition")
    print("=" * 70)
    
    # Check if templates exist
    template_dir = Path("poster_templates")
    if not template_dir.exists() or not list(template_dir.glob("*.jpg")) and not list(template_dir.glob("*.png")):
        print("\n⚠️  No templates found in poster_templates/")
        print("To test with templates:")
        print("  1. Create 'poster_templates/' directory")
        print("  2. Add movie poster images (.jpg or .png)")
        print("  3. Run this test again")
        return
    
    templates = list(template_dir.glob("*.jpg")) + list(template_dir.glob("*.png"))
    template_path = str(templates[0])
    
    print(f"Using template: {Path(template_path).name}")
    
    pipeline = Key2PosterPipeline(
        baseline_style=True,
        add_title=True,
        use_template=True,
        template_path=template_path,
        remove_text=False,
        super_resolution=False
    )
    
    pipeline._current_genre = "horror"
    
    output_path = "outputs/template_test/custom_template.png"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    image, brief, metrics = pipeline.generate_poster(
        "dark horror mansion",
        output_path=output_path,
        seed=123,
        evaluate=True
    )
    
    print(f"\n✅ Custom template test complete!")
    print(f"Saved to: {output_path}")
    print(f"Aesthetic score: {metrics['aesthetic']['overall']:.3f}")

def test_comparison():
    """Generate same poster with and without template"""
    print("\n" + "=" * 70)
    print("TEST: Comparison (With vs Without Template)")
    print("=" * 70)
    
    keywords = "cyberpunk neon city"
    seed = 999
    
    # Without template
    print("\n1. Generating WITHOUT template...")
    pipeline1 = Key2PosterPipeline(
        baseline_style=True,
        add_title=True,
        use_template=False,
        remove_text=False,
        super_resolution=False
    )
    pipeline1._current_genre = "scifi"
    
    output1 = "outputs/template_test/no_template.png"
    Path(output1).parent.mkdir(parents=True, exist_ok=True)
    
    image1, _, metrics1 = pipeline1.generate_poster(keywords, output1, seed=seed, evaluate=True)
    print(f"   Saved to: {output1}")
    
    # With simple layout
    print("\n2. Generating WITH simple layout...")
    pipeline2 = Key2PosterPipeline(
        baseline_style=True,
        add_title=True,
        use_template=True,
        template_path=None,
        remove_text=False,
        super_resolution=False
    )
    pipeline2._current_genre = "scifi"
    
    output2 = "outputs/template_test/with_template.png"
    
    image2, _, metrics2 = pipeline2.generate_poster(keywords, output2, seed=seed, evaluate=True)
    print(f"   Saved to: {output2}")
    
    print(f"\n✅ Comparison complete!")
    print(f"Without template: {metrics1['aesthetic']['overall']:.3f}")
    print(f"With template:    {metrics2['aesthetic']['overall']:.3f}")
    print(f"\nCompare the results in outputs/template_test/")

if __name__ == "__main__":
    import sys
    
    if "--template" in sys.argv:
        test_with_template()
    elif "--compare" in sys.argv:
        test_comparison()
    else:
        # Run simple layout test by default
        test_simple_layout()
        print("\n" + "=" * 70)
        print("Other test options:")
        print("  python test_template_composition.py --template  # Test with custom template")
        print("  python test_template_composition.py --compare   # Compare with/without template")
        print("=" * 70)
