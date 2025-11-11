"""Test complete pipeline functionality"""
import sys
from pathlib import Path

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        from src.concept_expander import ConceptExpander
        from src.visual_generator import VisualGenerator
        from src.evaluator import PosterEvaluator
        from src.refiner import QualityRefiner
        from src.pipeline import Key2PosterPipeline
        from src.lora_trainer import LoRATrainer
        from src.scraper import PosterScraper
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_concept_expander():
    """Test Agent 1: Concept Expander"""
    print("\nTesting Concept Expander Agent...")
    try:
        from src.concept_expander import ConceptExpander
        expander = ConceptExpander()
        brief = expander.expand("space exploration adventure")
        
        assert "keywords" in brief
        assert "sentiment" in brief
        assert "mood" in brief
        assert "prompt" in brief
        
        print(f"✓ Concept Expander working")
        print(f"  Sentiment: {brief['sentiment']}")
        print(f"  Mood: {brief['mood']}")
        return True
    except Exception as e:
        print(f"✗ Concept Expander failed: {e}")
        return False

def test_visual_generator():
    """Test Agent 2: Visual Generator"""
    print("\nTesting Visual Generator Agent...")
    try:
        from src.visual_generator import VisualGenerator
        import torch
        
        print(f"  CUDA available: {torch.cuda.is_available()}")
        print(f"  Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
        
        # Don't actually generate (too slow for test)
        generator = VisualGenerator()
        print("✓ Visual Generator initialized")
        return True
    except Exception as e:
        print(f"✗ Visual Generator failed: {e}")
        return False

def test_text_remover():
    """Test Agent 3: Text Remover"""
    print("\nTesting Text Remover Agent...")
    try:
        from src.text_remover import TextRemover
        from PIL import Image
        import numpy as np
        
        remover = TextRemover()
        
        # Create dummy image
        dummy_img = Image.fromarray(np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8))
        cleaned, text_found = remover.remove_text(dummy_img)
        
        assert cleaned.size == dummy_img.size
        print("✓ Text Remover working")
        return True
    except Exception as e:
        print(f"✗ Text Remover failed: {e}")
        return False

def test_refiner():
    """Test Agent 4: Quality Refiner"""
    print("\nTesting Quality Refiner Agent...")
    try:
        from src.refiner import QualityRefiner
        from PIL import Image
        import numpy as np
        
        refiner = QualityRefiner()
        
        # Create dummy image
        dummy_img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        refined = refiner.refine(dummy_img)
        
        assert refined.size == dummy_img.size
        print("✓ Quality Refiner working")
        return True
    except Exception as e:
        print(f"✗ Quality Refiner failed: {e}")
        return False

def test_evaluator():
    """Test Agent 5: Quality Evaluator"""
    print("\nTesting Quality Evaluator Agent...")
    try:
        from src.evaluator import PosterEvaluator
        from PIL import Image
        import numpy as np
        
        evaluator = PosterEvaluator()
        
        # Create dummy image
        dummy_img = Image.fromarray(np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8))
        dummy_path = "test_temp.png"
        dummy_img.save(dummy_path)
        
        metrics = evaluator.evaluate(dummy_path)
        
        assert "aesthetic" in metrics
        assert "resolution" in metrics
        
        # Cleanup
        Path(dummy_path).unlink()
        
        print("✓ Quality Evaluator working")
        print(f"  Aesthetic score: {metrics['aesthetic']['overall']:.3f}")
        return True
    except Exception as e:
        print(f"✗ Quality Evaluator failed: {e}")
        return False

def test_data_collection():
    """Test data collection capability"""
    print("\nTesting Data Collection...")
    try:
        from src.scraper import PosterScraper
        
        scraper = PosterScraper()
        movie_ids = scraper.get_top_movie_ids(count=5)
        
        assert len(movie_ids) == 5
        print(f"✓ Data collection ready ({len(movie_ids)} sample IDs)")
        return True
    except Exception as e:
        print(f"✗ Data collection failed: {e}")
        return False

def test_lora_trainer():
    """Test LoRA trainer initialization"""
    print("\nTesting LoRA Trainer...")
    try:
        from src.lora_trainer import LoRATrainer
        import torch
        
        print(f"  CUDA available: {torch.cuda.is_available()}")
        
        # Don't actually train (too slow for test)
        print("✓ LoRA Trainer module available")
        return True
    except Exception as e:
        print(f"✗ LoRA Trainer failed: {e}")
        return False

def test_pipeline():
    """Test complete pipeline initialization"""
    print("\nTesting Complete Pipeline...")
    try:
        from src.pipeline import Key2PosterPipeline
        
        pipeline = Key2PosterPipeline(use_lora=False)
        
        # Test keyword validation
        try:
            pipeline.generate_poster("single", evaluate=False)
            print("✗ Should reject single keyword")
            return False
        except ValueError:
            print("✓ Keyword validation working")
        
        print("✓ Pipeline initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        return False

def main():
    print("="*60)
    print("KEY2POSTER PIPELINE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Agent 1: Concept Expander", test_concept_expander),
        ("Agent 2: Visual Generator", test_visual_generator),
        ("Agent 3: Text Remover", test_text_remover),
        ("Agent 4: Quality Refiner", test_refiner),
        ("Agent 5: Quality Evaluator", test_evaluator),
        ("Data Collection", test_data_collection),
        ("LoRA Trainer", test_lora_trainer),
        ("Complete Pipeline", test_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Pipeline is ready.")
        print("\nNext steps:")
        print("  1. python src/collect_data.py    # Collect training data")
        print("  2. python src/train_lora.py      # Train LoRA model")
        print("  3. python run_pipeline.py 'your keywords' --lora")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
