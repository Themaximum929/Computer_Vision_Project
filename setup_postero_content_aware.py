"""
Setup script for PosterO Content-Aware Layout Generation
Downloads pre-trained design intent detection models
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

def setup_design_intent_models(output_dir="models/design_intent"):
    """Download pre-trained design intent detection models from HuggingFace"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("📥 Downloading pre-trained design intent detection models...")
    
    # Model repository (you'll need to upload or find the official weights)
    # For now, this is a placeholder - replace with actual HF repo
    models = {
        'pku': 'design_intent_pku_epoch100.pth',
        'cgl': 'design_intent_cgl_epoch35.pth',
        'all': 'design_intent_all_epoch25.pth'
    }
    
    for dataset, filename in models.items():
        try:
            # TODO: Replace with actual HuggingFace repo when available
            # model_path = hf_hub_download(
            #     repo_id="postero/design-intent-detection",
            #     filename=filename,
            #     local_dir=output_path
            # )
            print(f"⚠ Model for {dataset} not yet available on HuggingFace")
            print(f"  Please download manually from PosterO GitHub releases")
        except Exception as e:
            print(f"❌ Failed to download {dataset} model: {e}")
    
    print(f"\n✅ Models should be placed in: {output_path.absolute()}")
    print("\nManual download instructions:")
    print("1. Go to: https://github.com/theKinsley/PosterO-CVPR2025/releases")
    print("2. Download design intent detection weights")
    print(f"3. Place .pth files in: {output_path.absolute()}")

def check_dataset_structure(dataset_root):
    """Verify PKU/CGL dataset structure"""
    root = Path(dataset_root)
    
    required_dirs = [
        'pku/annotation',
        'pku/image/train/input',
        'pku/image/train/saliency',
        'pku/image/test/input',
        'pku/image/test/saliency'
    ]
    
    print(f"\n🔍 Checking dataset structure at: {root.absolute()}")
    
    missing = []
    for dir_path in required_dirs:
        full_path = root / dir_path
        if not full_path.exists():
            missing.append(dir_path)
            print(f"❌ Missing: {dir_path}")
        else:
            print(f"✅ Found: {dir_path}")
    
    if missing:
        print(f"\n⚠ Missing {len(missing)} required directories")
        print("\nSetup instructions:")
        print("1. Download PKU PosterLayout dataset")
        print("2. Run RALF preprocessing (inpainting + saliency detection)")
        print("3. Organize files according to PosterO structure")
        return False
    
    print("\n✅ Dataset structure is valid!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-root', default='/home/themaximum/Documents/GitHub/Computer_Vision_Project/src/Dataset/', help='Path to dataset root')
    parser.add_argument('--model-dir', default='./models/design_intent', help='Output dir for models')
    args = parser.parse_args()
    
    # Download models
    setup_design_intent_models(args.model_dir)
    
    # Check dataset
    if Path(args.dataset_root).exists():
        check_dataset_structure(args.dataset_root)
    else:
        print(f"\n⚠ Dataset root not found: {args.dataset_root}")
        print("Create it and add PKU/CGL datasets")
