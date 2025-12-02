# Linux Setup Guide - PosterO Training

Complete setup guide for training PosterO design intent detector on Linux.

## System Requirements

- Ubuntu 20.04+ or similar Linux distribution
- NVIDIA GPU with 8GB+ VRAM
- CUDA 11.8 or 12.1
- Python 3.8+

## Quick Setup

### Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git wget
```

### Step 2: Setup Project

```bash
# Clone/copy your project
cd ~/
git clone <your-repo> Computer_Vision_Project
cd Computer_Vision_Project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install PyTorch with CUDA

```bash
# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### Step 4: Install Project Dependencies

```bash
pip install -r requirements_linux.txt
```

### Step 5: Download PKU Dataset

```bash
# Install HuggingFace CLI
pip install huggingface-hub

# Download dataset
huggingface-cli download creative-graphic-design/PKU-PosterLayout \
  --repo-type dataset \
  --local-dir ~/poster_dataset/pku
```

### Step 6: Convert Dataset

```bash
# Copy conversion script to Linux paths
python convert_pku_dataset_linux.py
python fix_csv_format_linux.py
```

### Step 7: Train Design Intent Detector

```bash
cd ~/PosterO-CVPR2025/design_intent_detect

# Preprocess
python preprocess.py \
  --dataset_root ~/poster_dataset \
  --dataset pku

# Train
torchrun --nproc_per_node=1 main.py \
  --dataset_root ~/poster_dataset \
  --dataset pku \
  --epoch 100 \
  --batch_size 8 \
  --learning_rate 1e-4
```

Training takes 2-4 hours on RTX 3090.

### Step 8: Use Trained Model

```python
from src.postero_pipeline import PosterOPipeline

pipeline = PosterOPipeline(
    llm_path="~/models/mistral-7b",
    intent_model_path="~/PosterO-CVPR2025/design_intent_detect/checkpoints/best_model.pth",
    use_official=True
)

layout = pipeline.generate_layout(image, "cyberpunk city", num_elements=3)
```

## File Structure

```
~/
├── Computer_Vision_Project/
│   ├── src/
│   ├── templates/
│   ├── requirements_linux.txt
│   └── ...
├── PosterO-CVPR2025/
│   └── design_intent_detect/
├── poster_dataset/
│   └── pku/
│       ├── image/
│       └── annotation/
└── models/
    └── mistral-7b/
```

## Troubleshooting

### CUDA Not Available

```bash
# Check NVIDIA driver
nvidia-smi

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

### Out of Memory

```bash
# Reduce batch size
torchrun --nproc_per_node=1 main.py \
  --dataset_root ~/poster_dataset \
  --dataset pku \
  --epoch 100 \
  --batch_size 4 \
  --learning_rate 1e-4
```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements_linux.txt
```

## Performance

| GPU | Batch Size | Time/Epoch | Total Time |
|-----|-----------|------------|------------|
| RTX 4090 | 16 | ~5 min | ~8 hours |
| RTX 3090 | 8 | ~8 min | ~13 hours |
| RTX 3060 | 4 | ~15 min | ~25 hours |

## Next Steps

After training completes:

1. **Test the model:**
```bash
python main.py \
  --infer \
  --dataset_root ~/poster_dataset \
  --dataset pku \
  --infer_ckpt checkpoints/best_model.pth
```

2. **Generate posters with trained detector:**
```bash
cd ~/Computer_Vision_Project
python app_template.py
```

3. **Use in production:**
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    use_flux=True,
    intent_model_path="~/PosterO-CVPR2025/design_intent_detect/checkpoints/best_model.pth"
)

image, brief, metrics = pipeline.generate_poster(
    "cyberpunk neon city",
    output_path="poster.png"
)
```

## Summary

```bash
# Complete setup in one go
sudo apt update && sudo apt install -y python3-pip python3-venv
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements_linux.txt
huggingface-cli download creative-graphic-design/PKU-PosterLayout --repo-type dataset --local-dir ~/poster_dataset/pku
python convert_pku_dataset_linux.py
python fix_csv_format_linux.py
cd ~/PosterO-CVPR2025/design_intent_detect
python preprocess.py --dataset_root ~/poster_dataset --dataset pku
torchrun --nproc_per_node=1 main.py --dataset_root ~/poster_dataset --dataset pku --epoch 100 --batch_size 8 --learning_rate 1e-4
```

Done! 🚀
