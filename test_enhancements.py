"""Test Enhanced Features"""
from src.pipeline import Key2PosterPipeline
from src.template_manager import TemplateManager
from src.color_palette_extractor import ColorPaletteExtractor
from src.composition_engine import CompositionEngine
from pathlib import Path

def test_template_system():
    """Test template manager"""
    print("\n=== Testing Template System ===")
    manager = TemplateManager()
    templates = manager.get_template_list()
    print(f"Available templates: {templates}")
    assert len(templates) >= 4, "Should have at least 4 templates"
    print("✓ Template system working")

def test_color_extraction():
    """Test color palette extraction"""
    print("\n=== Testing Color Extraction ===")
    from PIL import Image
    
    # Create test image
    test_img = Image.new('RGB', (512, 512), (100, 150, 200))
    
    extractor = ColorPaletteExtractor()
    palette = extractor.extract_palette(test_img, n_colors=5)
    mood = extractor.analyze_mood_from_colors()
    accent = extractor.get_accent_color()
    
    print(f"Extracted palette: {palette[:3]}")
    print(f"Detected mood: {mood}")
    print(f"Accent color: {accent}")
    
    assert len(palette) == 5, "Should extract 5 colors"
    assert mood in ["intense", "calm", "energetic", "dark", "balanced"], "Valid mood"
    print("✓ Color extraction working")

def test_composition_engine():
    """Test composition engine"""
    print("\n=== Testing Composition Engine ===")
    from PIL import Image
    
    test_img = Image.new('RGB', (720, 1280), (50, 50, 50))
    
    engine = CompositionEngine()
    safe_zones = engine.detect_safe_zones(test_img)
    position, brightness = engine.get_best_title_position(test_img)
    enhanced = engine.add_vignette(test_img, strength=0.3)
    
    print(f"Detected {len(safe_zones)} safe zones")
    print(f"Best position: {position}, brightness: {brightness}")
    print(f"Vignette applied: {enhanced.size}")
    
    assert len(safe_zones) > 0, "Should detect safe zones"
    assert enhanced.size == test_img.size, "Size should match"
    print("✓ Composition engine working")

def test_full_integration():
    """Test full enhanced pipeline"""
    print("\n=== Testing Full Integration ===")
    
    # Generate base poster
    pipeline = Key2PosterPipeline(
        genre_lora=True,
        add_title=False,
        aggressive_text_removal=True,
        super_resolution=False
    )
    
    output_dir = Path("outputs/enhancement_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    keywords = "cyberpunk neon city"
    print(f"Generating poster for: {keywords}")
    
    image, brief, metrics = pipeline.generate_poster(
        keywords,
        output_path=str(output_dir / "base.png"),
        seed=42,
        evaluate=True
    )
    
    print(f"Base poster generated: {image.size}")
    
    # Apply enhancements
    template_manager = TemplateManager()
    color_extractor = ColorPaletteExtractor()
    composition_engine = CompositionEngine()
    
    # Extract colors
    palette = color_extractor.extract_palette(image)
    mood = color_extractor.analyze_mood_from_colors()
    print(f"Color mood: {mood}")
    
    # Apply template
    image_templated = template_manager.apply_template(image, "minimal", keywords)
    image_templated.save(output_dir / "templated.png")
    print("✓ Template applied")
    
    # Add vignette
    image_vignette = composition_engine.add_vignette(image, strength=0.3)
    image_vignette.save(output_dir / "vignette.png")
    print("✓ Vignette applied")
    
    # Composition guide
    image_guide = composition_engine.apply_rule_of_thirds_grid(image, show_grid=True)
    image_guide.save(output_dir / "composition_guide.png")
    print("✓ Composition guide created")
    
    print(f"\n✓ All enhancements saved to {output_dir}")
    print("\nGenerated files:")
    print("  - base.png (original)")
    print("  - templated.png (with template)")
    print("  - vignette.png (with vignette)")
    print("  - composition_guide.png (with grid)")

if __name__ == "__main__":
    print("Testing Key2Poster Enhancements")
    print("=" * 50)
    
    try:
        test_template_system()
        test_color_extraction()
        test_composition_engine()
        test_full_integration()
        
        print("\n" + "=" * 50)
        print("✅ All enhancement tests passed!")
        print("\nNext steps:")
        print("1. Run: python app_enhanced.py")
        print("2. Try different templates and effects")
        print("3. Check outputs/enhancement_test/ for examples")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
