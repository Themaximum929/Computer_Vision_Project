"""Test script to verify setup and dependencies"""
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
        return False
    
    try:
        import diffusers
        print(f"✓ Diffusers {diffusers.__version__}")
    except ImportError as e:
        print(f"✗ Diffusers: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    try:
        import requests
        print(f"✓ Requests")
    except ImportError as e:
        print(f"✗ Requests: {e}")
        return False
    
    return True

def test_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    
    try:
        from src.concept_expander import ConceptExpander
        print("✓ ConceptExpander")
    except Exception as e:
        print(f"✗ ConceptExpander: {e}")
        return False
    
    try:
        from src.visual_generator import VisualGenerator
        print("✓ VisualGenerator")
    except Exception as e:
        print(f"✗ VisualGenerator: {e}")
        return False
    
    try:
        from src.evaluator import PosterEvaluator
        print("✓ PosterEvaluator")
    except Exception as e:
        print(f"✗ PosterEvaluator: {e}")
        return False
    
    try:
        from src.scraper import PosterScraper
        print("✓ PosterScraper")
    except Exception as e:
        print(f"✗ PosterScraper: {e}")
        return False
    
    try:
        from src.pipeline import Key2PosterPipeline
        print("✓ Key2PosterPipeline")
    except Exception as e:
        print(f"✗ Key2PosterPipeline: {e}")
        return False
    
    return True

def test_concept_expander():
    """Test concept expander functionality"""
    print("\nTesting ConceptExpander...")
    
    try:
        from src.concept_expander import ConceptExpander
        expander = ConceptExpander()
        brief = expander.expand("space exploration adventure")
        
        assert "keywords" in brief
        assert "prompt" in brief
        print("✓ ConceptExpander working")
        print(f"  Sample output: {brief['prompt'][:80]}...")
        return True
    except Exception as e:
        print(f"✗ ConceptExpander test failed: {e}")
        return False

def main():
    print("="*60)
    print("KEY2POSTER SETUP TEST")
    print("="*60)
    
    # Test imports
    if not test_imports():
        print("\n✗ Import test failed. Please install requirements:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Test modules
    if not test_modules():
        print("\n✗ Module test failed. Check project structure.")
        sys.exit(1)
    
    # Test functionality
    if not test_concept_expander():
        print("\n✗ Functionality test failed.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nYou're ready to use Key2Poster!")
    print("\nNext steps:")
    print("  1. Run demo: python demo.py")
    print("  2. Collect data: python src/collect_data.py")
    print("  3. Train LoRA: python src/train_lora.py")
    print("  4. Run experiments: python src/experiment.py")

if __name__ == "__main__":
    main()
