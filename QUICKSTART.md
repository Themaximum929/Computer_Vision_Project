# Key2Poster Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Setup
```bash
python test_setup.py
```

### 3. Run Demo
```bash
python demo.py
```

## 📋 Complete Workflow (Step-by-Step)

### Step 1: Baseline Experiment
```bash
# Generate posters with vanilla Stable Diffusion
python demo.py
```
**Output**: `outputs/demo/poster_*.png`

### Step 2: Collect Training Data
```bash
# Scrape ~25 movie posters from IMDB
python src/collect_data.py
```
**Output**: `data/posters/poster_*.jpg`

### Step 3: Train LoRA
```bash
# Fine-tune SD on collected posters (~10 epochs)
python src/train_lora.py
```
**Output**: `models/poster_lora/`
**Time**: ~30-60 minutes on GPU

### Step 4: Run Experiments
```bash
# Compare baseline vs LoRA
python src/experiment.py
```
**Output**: 
- `outputs/baseline/poster_*.png`
- `outputs/lora/poster_*.png`
- `outputs/*/results.json`

## 🎯 Expected Results

### Baseline (Vanilla SD)
- Generic poster-like images
- Good quality but not poster-specific style
- Aesthetic score: ~0.4-0.6

### LoRA (Fine-tuned)
- More poster-specific aesthetics
- Better composition and style
- Aesthetic score: ~0.5-0.7 (improvement expected)

## 📊 Evaluation

Results are automatically saved in JSON format:
```json
{
  "keywords": "space exploration adventure",
  "metrics": {
    "aesthetic": {
      "overall": 0.542,
      "color_variance": 1234.5,
      "brightness_balance": 0.87
    },
    "resolution": {
      "width": 512,
      "height": 768
    }
  }
}
```

## 🔧 Customization

### Change Test Keywords
Edit `src/experiment.py`:
```python
test_keywords = [
    "your custom keyword 1",
    "your custom keyword 2",
    # ...
]
```

### Adjust Generation Parameters
Edit `src/visual_generator.py`:
```python
def generate(self, 
    prompt, 
    width=512,           # Change resolution
    height=768,
    num_inference_steps=30,  # More steps = better quality
    guidance_scale=7.5   # Higher = more prompt adherence
):
```

### Modify Training
Edit `src/train_lora.py`:
```python
trainer.train(
    epochs=10,      # More epochs = better fit
    batch_size=1,   # Increase if you have GPU memory
    lr=1e-4         # Learning rate
)
```

## 💡 Tips

1. **GPU Recommended**: Training and generation are much faster on GPU
2. **Start Small**: Test with demo before full experiments
3. **Save Seeds**: Use same seed for reproducible comparisons
4. **Monitor Memory**: Reduce batch_size if out of memory
5. **Be Patient**: First run downloads ~4GB model

## 🐛 Troubleshooting

### "No module named 'src'"
```bash
# Make sure you're in project root
cd Computer_Vision_Project
python demo.py
```

### "CUDA out of memory"
```python
# In visual_generator.py, use CPU
self.device = "cpu"
```

### "No training data found"
```bash
# Run data collection first
python src/collect_data.py
```

### Slow generation
```python
# Reduce inference steps
num_inference_steps=20  # Instead of 30
```

## 📁 File Structure
```
Computer_Vision_Project/
├── demo.py              ← Start here
├── test_setup.py        ← Verify setup
├── src/
│   ├── collect_data.py  ← Step 2
│   ├── train_lora.py    ← Step 3
│   └── experiment.py    ← Step 4
├── outputs/             ← Generated posters
└── data/posters/        ← Training data
```

## ⏱️ Time Estimates

- Setup: 5 minutes
- Demo: 2-3 minutes per poster
- Data collection: 5-10 minutes
- LoRA training: 30-60 minutes (GPU)
- Experiments: 10-15 minutes

## 🎓 For Grading

1. Run baseline experiment
2. Collect data (100+ images recommended)
3. Train LoRA
4. Run comparative experiments
5. Document results in report

**Target**: Level 2-3 (70-90 points)
