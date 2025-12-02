# Setup After Cloning from GitHub

This guide helps you reinstall large files after cloning the repository.

## What's Excluded from Git

- Models (~15GB): Mistral-7B, FLUX
- Dataset (~20GB): PKU PosterLayout
- Generated outputs
- Python virtual environment

## Quick Setup on Linux

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Computer_Vision_Project

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. Install dependencies
pip install -r requirements_linux.txt

# 5. Download Mistral-7B model
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ~/models/mistral-7b

# 6. Download PKU dataset
huggingface-cli download creative-graphic-design/PKU-PosterLayout --repo-type dataset --local-dir ~/poster_dataset/pku

# 7. Convert dataset
python convert_pku_dataset_linux.py
python fix_csv_format_linux.py

# 8. Download PosterO repository
cd ~
git clone https://github.com/theKinsley/PosterO-CVPR2025.git

# 9. Train design intent detector (optional, 2-4 hours)
cd ~/PosterO-CVPR2025/design_intent_detect
python preprocess.py --dataset_root ~/poster_dataset --dataset pku
torchrun --nproc_per_node=1 main.py --dataset_root ~/poster_dataset --dataset pku --epoch 100 --batch_size 8 --learning_rate 1e-4

# 10. Test the system
cd ~/Computer_Vision_Project
python demo_postero_llm.py
```

## File Sizes

| Item | Size | Download Time (100Mbps) |
|------|------|------------------------|
| Mistral-7B | ~15GB | ~20 min |
| PKU Dataset | ~20GB | ~30 min |
| Dependencies | ~5GB | ~7 min |
| **Total** | **~40GB** | **~1 hour** |

## Directory Structure After Setup

```
~/
├── Computer_Vision_Project/          # Your cloned repo
│   ├── src/
│   ├── templates/
│   ├── venv/                         # Created locally
│   └── requirements_linux.txt
├── models/                           # Downloaded separately
│   └── mistral-7b/
├── poster_dataset/                   # Downloaded separately
│   └── pku/
└── PosterO-CVPR2025/                # Cloned separately
    └── design_intent_detect/
```

## Verification

```bash
# Check PyTorch + CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check models
ls ~/models/mistral-7b/

# Check dataset
ls ~/poster_dataset/pku/image/train/input/ | wc -l  # Should show ~9975

# Test generation
cd ~/Computer_Vision_Project
python demo_postero_llm.py
```

## Troubleshooting

### CUDA Not Available
```bash
nvidia-smi  # Check GPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
```

### Dataset Not Found
```bash
# Re-download
huggingface-cli download creative-graphic-design/PKU-PosterLayout --repo-type dataset --local-dir ~/poster_dataset/pku
python convert_pku_dataset_linux.py
```

### Model Not Found
```bash
# Re-download
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ~/models/mistral-7b
```

## One-Line Setup

```bash
git clone <repo> && cd Computer_Vision_Project && python3 -m venv venv && source venv/bin/activate && pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 && pip install -r requirements_linux.txt && huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ~/models/mistral-7b && huggingface-cli download creative-graphic-design/PKU-PosterLayout --repo-type dataset --local-dir ~/poster_dataset/pku && python convert_pku_dataset_linux.py && python fix_csv_format_linux.py && python demo_postero_llm.py
```

## What's Included in Git

✅ Source code  
✅ Configuration files  
✅ Template JSON files  
✅ Documentation  
✅ Setup scripts  

## What You Need to Download

❌ Models (15GB)  
❌ Dataset (20GB)  
❌ Virtual environment  
❌ Generated outputs  

Total download: ~40GB, ~1 hour on 100Mbps connection.

🚀 Ready to generate posters!
