# Models Directory

This directory contains trained LoRA models for genre-specific poster generation.

## Required Structure

```
models/
├── lora_action/
│   └── lora_weights.pth
├── lora_comedy/
│   └── lora_weights.pth
├── lora_fantasy/
│   └── lora_weights.pth
├── lora_horror/
│   └── lora_weights.pth
├── lora_romance/
│   └── lora_weights.pth
├── lora_scifi/
│   └── lora_weights.pth
└── lora_general/
    └── lora_weights.pth
```

## Download Models

**Models are NOT included in the repository due to size (~500MB each).**

### Option 1: Download Pre-trained Models
Contact the project maintainer for access to pre-trained LoRA models.

### Option 2: Train Your Own
```bash
# Collect training data
python src/collect_data.py

# Preprocess data
python preprocess_training_data.py

# Train models by genre
python train_by_genre.py
```

## Model Details

- **Base Model:** Stable Diffusion v1.5
- **LoRA Rank:** 16
- **Training Steps:** ~1000 per genre
- **File Size:** ~500MB per genre
- **Format:** PyTorch (.pth)

## Without Models

The application will work without LoRA models but will use baseline Stable Diffusion (no genre-specific styling).
