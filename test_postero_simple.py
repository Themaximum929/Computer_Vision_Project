#!/usr/bin/env python3
"""
Simple test for PosterO layout generation
Tests if the pipeline.py from classmate's work is functional
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src" / "generalized_setting"))

def test_postero_imports():
    """Test if PosterO modules can be imported"""
    print("Testing PosterO imports...")
    
    try:
        from pipeline import LayoutGenerationPipeline
        print("✓ LayoutGenerationPipeline imported")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_postero_generation():
    """Test PosterO layout generation with dummy data"""
    print("\nTesting PosterO layout generation...")
    
    try:
        from pipeline import LayoutGenerationPipeline
        
        # Minimal dataset info
        dataset_info = {
            'dataset_name': 'pstylish7_movie-poster',
            'design_intent_bbox_dir': './PStylish7/movie-poster/predm_zs',
            'annotation_dir': './PStylish7/movie-poster',
            'label_info': {
                'T-G': {'type': 'text-general', 'color': 'green'},
                'L': {'type': 'logo', 'color': 'red'},
            }
        }
        
        print("Creating pipeline...")
        pipeline = LayoutGenerationPipeline(
            dataset_info=dataset_info,
            canvas_size=(512, 768),
            sample_size=3
        )
        print("✓ Pipeline created")
        
        # Test with dummy image path and bboxes
        print("\nGenerating layout...")
        result = pipeline.generate_layout(
            image="test.png",  # Dummy path
            design_intent_bboxes=[(50, 50, 450, 200), (50, 600, 450, 720)],
            num_generations=1
        )
        
        print("✓ Layout generated")
        print(f"  Elements: {result['layout_graphs'][0]['cls_elem']}")
        print(f"  Bboxes: {result['layout_graphs'][0]['box_elem']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("PosterO Simple Test")
    print("="*60)
    
    # Test imports
    if not test_postero_imports():
        print("\n❌ Import test failed")
        print("Make sure you're in the correct directory and dependencies are installed")
        sys.exit(1)
    
    # Test generation
    if not test_postero_generation():
        print("\n❌ Generation test failed")
        print("Check if PStylish7 dataset is available and LLM API is configured")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
