"""Check if PosterO Generalized setup is ready"""
import os
import sys

def check_setup():
    """Verify all requirements for PosterO Generalized"""
    
    print("=" * 60)
    print("PosterO Generalized Setup Checker")
    print("=" * 60)
    
    checks = []
    
    # 1. Check PStylish7 dataset
    print("\n[1/6] Checking PStylish7 dataset...")
    dataset_path = "/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
    categories = ['chinese-poem', 'food-menu', 'kind-animals', 'london-subway', 
                  'motivational-quote', 'movie-poster', 'travel-vintage']
    
    if os.path.exists(dataset_path):
        print(f"  ✓ Dataset found at {dataset_path}")
        missing = []
        for cat in categories:
            cat_path = os.path.join(dataset_path, cat)
            if not os.path.exists(cat_path):
                missing.append(cat)
        
        if missing:
            print(f"  ✗ Missing categories: {', '.join(missing)}")
            checks.append(False)
        else:
            print(f"  ✓ All 7 categories present")
            checks.append(True)
    else:
        print(f"  ✗ Dataset not found at {dataset_path}")
        checks.append(False)
    
    # 2. Check PosterO source
    print("\n[2/6] Checking PosterO source code...")
    postero_path = "/home/themaximum/Documents/GitHub/PosterO-CVPR2025/generalized_setting"
    
    if os.path.exists(postero_path):
        print(f"  ✓ PosterO source found at {postero_path}")
        checks.append(True)
    else:
        print(f"  ✗ PosterO source not found at {postero_path}")
        checks.append(False)
    
    # 3. Check integration files
    print("\n[3/6] Checking integration files...")
    integration_files = [
        'src/postero_generalized.py',
        'test_postero_generalized.py',
        'run_postero_generalized.sh',
        'app_postero_generalized.py',
        'POSTERO_GENERALIZED_QUICKSTART.md'
    ]
    
    missing_files = []
    for f in integration_files:
        if not os.path.exists(f):
            missing_files.append(f)
    
    if missing_files:
        print(f"  ✗ Missing files: {', '.join(missing_files)}")
        checks.append(False)
    else:
        print(f"  ✓ All integration files present")
        checks.append(True)
    
    # 4. Check Python dependencies
    print("\n[4/6] Checking Python dependencies...")
    required = ['torch', 'transformers', 'PIL', 'numpy']
    optional = ['vllm']
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"  ✗ Missing required packages: {', '.join(missing)}")
        checks.append(False)
    else:
        print(f"  ✓ All required packages installed")
        
        # Check optional
        try:
            __import__('vllm')
            print(f"  ✓ vLLM installed (recommended)")
        except ImportError:
            print(f"  ⚠ vLLM not installed (optional but recommended)")
        
        checks.append(True)
    
    # 5. Check Mistral path
    print("\n[5/6] Checking Mistral-7B path...")
    print("  ⚠ You need to update Mistral path in:")
    print("    - run_postero_generalized.sh")
    print("    - app_postero_generalized.py")
    print("    - test_postero_generalized.py")
    print("  ℹ Current placeholder: /path/to/mistral-7b")
    checks.append(None)  # Manual check
    
    # 6. Check GPU
    print("\n[6/6] Checking GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"  ✓ GPU available: {gpu_name}")
            print(f"  ✓ VRAM: {gpu_memory:.1f} GB")
            if gpu_memory < 16:
                print(f"  ⚠ Recommended: 16GB+ VRAM (you have {gpu_memory:.1f}GB)")
            checks.append(True)
        else:
            print(f"  ✗ No GPU available (CUDA not detected)")
            checks.append(False)
    except:
        print(f"  ✗ Cannot check GPU (torch not installed)")
        checks.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for c in checks if c is True)
    failed = sum(1 for c in checks if c is False)
    manual = sum(1 for c in checks if c is None)
    
    print(f"Passed: {passed}/{len(checks)}")
    print(f"Failed: {failed}/{len(checks)}")
    print(f"Manual: {manual}/{len(checks)}")
    
    if failed == 0 and manual <= 1:
        print("\n✓ Setup is ready!")
        print("\nNext steps:")
        print("1. Update Mistral path in scripts")
        print("2. Run: python test_postero_generalized.py")
        print("3. Or run: ./run_postero_generalized.sh")
    else:
        print("\n✗ Setup incomplete. Please fix the issues above.")
        print("\nSee POSTERO_GENERALIZED_QUICKSTART.md for help")
    
    print("=" * 60)

if __name__ == "__main__":
    check_setup()
