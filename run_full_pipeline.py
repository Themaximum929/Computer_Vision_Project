"""Run complete end-to-end pipeline: Data Collection → Training → Generation → Evaluation"""
import sys
import argparse
from pathlib import Path

def check_data_exists():
    """Check if training data exists"""
    data_dir = Path("data/posters")
    if not data_dir.exists():
        return False
    images = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.png"))
    return len(images) > 0

def check_model_exists():
    """Check if LoRA model exists"""
    model_path = Path("models/poster_lora/lora_weights.pth")
    return model_path.exists()

def run_data_collection():
    """Step 1: Collect training data"""
    print("\n" + "="*60)
    print("STEP 1: DATA COLLECTION")
    print("="*60)
    
    if check_data_exists():
        print("✓ Training data already exists in data/posters/")
        response = input("Collect more data? (y/n): ")
        if response.lower() != 'y':
            return True
    
    try:
        from src.collect_data import main as collect_main
        collect_main()
        return True
    except Exception as e:
        print(f"✗ Data collection failed: {e}")
        return False

def run_training():
    """Step 2: Train LoRA model"""
    print("\n" + "="*60)
    print("STEP 2: LORA TRAINING")
    print("="*60)
    
    if not check_data_exists():
        print("✗ No training data found. Run data collection first.")
        return False
    
    if check_model_exists():
        print("✓ LoRA model already exists in models/poster_lora/")
        response = input("Retrain model? (y/n): ")
        if response.lower() != 'y':
            return True
    
    try:
        from src.train_lora import main as train_main
        train_main()
        return True
    except Exception as e:
        print(f"✗ Training failed: {e}")
        return False

def run_generation(test_mode=False):
    """Step 3: Generate posters"""
    print("\n" + "="*60)
    print("STEP 3: POSTER GENERATION")
    print("="*60)
    
    if not check_model_exists():
        print("⚠ LoRA model not found. Using baseline model only.")
        use_lora = False
    else:
        use_lora = True
    
    try:
        from src.pipeline import Key2PosterPipeline
        
        # Test keywords
        test_keywords = [
            "space exploration adventure",
            "dark fantasy warrior",
            "romantic sunset beach"
        ]
        
        if test_mode:
            print("\nGenerating test posters...")
            pipeline = Key2PosterPipeline(
                use_lora=use_lora,
                lora_path="models/poster_lora" if use_lora else None
            )
            
            for i, keywords in enumerate(test_keywords):
                output_path = f"outputs/pipeline_test/poster_{i}.png"
                print(f"\n[{i+1}/{len(test_keywords)}] Generating: {keywords}")
                image, brief, metrics = pipeline.generate_poster(keywords, output_path)
        else:
            # Interactive mode
            keywords = input("\nEnter 2-5 keywords: ")
            output_path = input("Output path (default: outputs/poster.png): ") or "outputs/poster.png"
            
            pipeline = Key2PosterPipeline(
                use_lora=use_lora,
                lora_path="models/poster_lora" if use_lora else None
            )
            
            image, brief, metrics = pipeline.generate_poster(keywords, output_path)
        
        return True
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return False

def run_evaluation():
    """Step 4: Run baseline vs LoRA comparison"""
    print("\n" + "="*60)
    print("STEP 4: EVALUATION (Baseline vs LoRA)")
    print("="*60)
    
    if not check_model_exists():
        print("✗ LoRA model not found. Cannot run comparison.")
        print("  Run training first: python src/train_lora.py")
        return False
    
    response = input("Run full comparison experiment? This will take 10-20 minutes. (y/n): ")
    if response.lower() != 'y':
        print("Skipping evaluation.")
        return True
    
    try:
        from src.experiment import run_comparison_experiment
        
        test_keywords = [
            "space exploration adventure",
            "dark fantasy warrior",
            "romantic sunset beach",
            "cyberpunk city noir",
            "epic battle scene"
        ]
        
        results = run_comparison_experiment(test_keywords)
        return True
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run complete Key2Poster pipeline")
    parser.add_argument("--skip-data", action="store_true", help="Skip data collection")
    parser.add_argument("--skip-training", action="store_true", help="Skip LoRA training")
    parser.add_argument("--skip-generation", action="store_true", help="Skip poster generation")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip evaluation")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (auto-generate test posters)")
    args = parser.parse_args()
    
    print("="*60)
    print("KEY2POSTER: COMPLETE PIPELINE")
    print("="*60)
    print("\nThis will run the complete pipeline:")
    print("  1. Data Collection (2 minutes)")
    print("  2. LoRA Training (10-30 minutes)")
    print("  3. Poster Generation")
    print("  4. Evaluation (optional)")
    print()
    
    # Step 1: Data Collection
    if not args.skip_data:
        if not run_data_collection():
            print("\n✗ Pipeline failed at data collection")
            sys.exit(1)
    else:
        print("\nSkipping data collection...")
    
    # Step 2: Training
    if not args.skip_training:
        if not run_training():
            print("\n✗ Pipeline failed at training")
            sys.exit(1)
    else:
        print("\nSkipping training...")
    
    # Step 3: Generation
    if not args.skip_generation:
        if not run_generation(test_mode=args.test_mode):
            print("\n✗ Pipeline failed at generation")
            sys.exit(1)
    else:
        print("\nSkipping generation...")
    
    # Step 4: Evaluation
    if not args.skip_evaluation:
        run_evaluation()  # Optional, don't fail pipeline
    else:
        print("\nSkipping evaluation...")
    
    print("\n" + "="*60)
    print("✓ PIPELINE COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - Training data: data/posters/")
    print("  - LoRA weights: models/poster_lora/")
    print("  - Generated posters: outputs/")
    print("\nNext steps:")
    print("  - Generate custom posters: python run_pipeline.py 'your keywords' --lora")
    print("  - Run experiments: python src/experiment.py")
    print("  - Quick demo: python demo.py")

if __name__ == "__main__":
    main()
